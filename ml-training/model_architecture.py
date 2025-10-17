"""
Model Architecture for Multi-label Skin Condition Classification
Supports both condition detection and severity prediction
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import timm
from typing import Dict, List, Optional, Tuple


class MultiLabelSkinClassifier(nn.Module):
    """
    Multi-label skin condition classifier with severity prediction
    
    Architecture:
    - Backbone: Pre-trained CNN (ResNet, EfficientNet, etc.)
    - Classification Head: Multi-label binary classification for 7 conditions
    - Severity Head: Multi-class classification for severity levels
    """
    
    def __init__(self, 
                 backbone_name: str = 'resnet50',
                 num_conditions: int = 7,
                 num_severity_levels: int = 6,
                 dropout_rate: float = 0.3,
                 pretrained: bool = True):
        super(MultiLabelSkinClassifier, self).__init__()
        
        self.backbone_name = backbone_name
        self.num_conditions = num_conditions
        self.num_severity_levels = num_severity_levels
        
        # Load pre-trained backbone
        self.backbone = timm.create_model(
            backbone_name, 
            pretrained=pretrained,
            num_classes=0  # Remove classifier head
        )
        
        # Get feature dimension from backbone
        self.feature_dim = self.backbone.num_features
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        
        # Classification head for condition detection
        self.classification_head = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(self.feature_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(512, num_conditions),
            nn.Sigmoid()  # Multi-label classification
        )
        
        # Severity prediction head (for each condition)
        self.severity_head = nn.ModuleList([
            nn.Sequential(
                nn.Dropout(dropout_rate),
                nn.Linear(self.feature_dim, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
                nn.Linear(256, num_severity_levels + 1)  # +1 for "no condition"
            ) for _ in range(num_conditions)
        ])
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights for custom heads"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch_size, 3, height, width)
            
        Returns:
            Dictionary containing:
            - condition_logits: Binary classification logits for each condition
            - severity_logits: Severity classification logits for each condition
            - features: Extracted features from backbone
        """
        # Extract features using backbone
        features = self.backbone.forward_features(x)
        
        # Global average pooling
        pooled_features = self.global_pool(features)
        pooled_features = pooled_features.view(pooled_features.size(0), -1)
        
        # Condition classification
        condition_logits = self.classification_head(pooled_features)
        
        # Severity prediction for each condition
        severity_logits = []
        for i in range(self.num_conditions):
            severity_logit = self.severity_head[i](pooled_features)
            severity_logits.append(severity_logit)
        
        severity_logits = torch.stack(severity_logits, dim=1)  # (batch, num_conditions, num_severity_levels+1)
        
        return {
            'condition_logits': condition_logits,
            'severity_logits': severity_logits,
            'features': pooled_features
        }


class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance in multi-label classification
    """
    
    def __init__(self, alpha: float = 1.0, gamma: float = 2.0, reduction: str = 'mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            inputs: Predicted probabilities (batch_size, num_classes)
            targets: Ground truth labels (batch_size, num_classes)
        """
        bce_loss = F.binary_cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-bce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * bce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class CombinedLoss(nn.Module):
    """
    Combined loss function for multi-label classification and severity prediction
    """
    
    def __init__(self, 
                 condition_weight: float = 1.0,
                 severity_weight: float = 0.5,
                 use_focal_loss: bool = True):
        super(CombinedLoss, self).__init__()
        
        self.condition_weight = condition_weight
        self.severity_weight = severity_weight
        
        if use_focal_loss:
            self.condition_loss = FocalLoss(alpha=1.0, gamma=2.0)
        else:
            self.condition_loss = nn.BCELoss()
        
        self.severity_loss = nn.CrossEntropyLoss(ignore_index=-1)
    
    def forward(self, 
                condition_logits: torch.Tensor, 
                severity_logits: torch.Tensor,
                condition_targets: torch.Tensor,
                severity_targets: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Compute combined loss
        
        Args:
            condition_logits: Predicted condition probabilities (batch, num_conditions)
            severity_logits: Predicted severity logits (batch, num_conditions, num_severity_levels+1)
            condition_targets: Ground truth condition labels (batch, num_conditions)
            severity_targets: Ground truth severity labels (batch, num_conditions)
        """
        # Condition classification loss
        condition_loss = self.condition_loss(condition_logits, condition_targets)
        
        # Severity prediction loss (only for present conditions)
        batch_size, num_conditions, num_severity_levels = severity_logits.shape
        
        # Reshape for cross-entropy loss
        severity_logits_flat = severity_logits.view(-1, num_severity_levels)
        severity_targets_flat = severity_targets.view(-1)
        
        # Only compute loss for valid severity targets (not -1)
        valid_mask = severity_targets_flat >= 0
        if valid_mask.sum() > 0:
            severity_loss = self.severity_loss(
                severity_logits_flat[valid_mask], 
                severity_targets_flat[valid_mask]
            )
        else:
            severity_loss = torch.tensor(0.0, device=condition_logits.device)
        
        # Combined loss
        total_loss = (self.condition_weight * condition_loss + 
                     self.severity_weight * severity_loss)
        
        return {
            'total_loss': total_loss,
            'condition_loss': condition_loss,
            'severity_loss': severity_loss
        }


class ModelMetrics:
    """
    Calculate metrics for multi-label classification
    """
    
    def __init__(self, num_conditions: int = 7, condition_names: Optional[List[str]] = None):
        self.num_conditions = num_conditions
        self.condition_names = condition_names or [
            'acne', 'aging', 'fine_lines_wrinkles', 'hyperpigmentation',
            'pore_size', 'redness', 'textured_skin'
        ]
        
        # Initialize metrics storage
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.predictions = []
        self.targets = []
        self.condition_predictions = []
        self.condition_targets = []
    
    def update(self, 
               condition_logits: torch.Tensor, 
               severity_logits: torch.Tensor,
               condition_targets: torch.Tensor,
               severity_targets: torch.Tensor):
        """Update metrics with batch predictions"""
        # Store predictions and targets
        self.predictions.append(condition_logits.detach().cpu())
        self.targets.append(condition_targets.detach().cpu())
        
        # Store condition-specific predictions
        condition_preds = (condition_logits > 0.5).float()
        self.condition_predictions.append(condition_preds.detach().cpu())
        self.condition_targets.append(condition_targets.detach().cpu())
    
    def compute_metrics(self) -> Dict[str, float]:
        """Compute final metrics"""
        if not self.predictions:
            return {}
        
        # Concatenate all predictions and targets
        all_preds = torch.cat(self.predictions, dim=0)
        all_targets = torch.cat(self.targets, dim=0)
        all_condition_preds = torch.cat(self.condition_predictions, dim=0)
        all_condition_targets = torch.cat(self.condition_targets, dim=0)
        
        metrics = {}
        
        # Overall metrics
        metrics['accuracy'] = (all_condition_preds == all_condition_targets).float().mean().item()
        
        # Per-condition metrics
        for i, condition in enumerate(self.condition_names):
            condition_pred = all_condition_preds[:, i]
            condition_target = all_condition_targets[:, i]
            
            # Precision, Recall, F1
            tp = (condition_pred * condition_target).sum().item()
            fp = (condition_pred * (1 - condition_target)).sum().item()
            fn = ((1 - condition_pred) * condition_target).sum().item()
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            metrics[f'{condition}_precision'] = precision
            metrics[f'{condition}_recall'] = recall
            metrics[f'{condition}_f1'] = f1
        
        # Macro averages
        precisions = [metrics[f'{condition}_precision'] for condition in self.condition_names]
        recalls = [metrics[f'{condition}_recall'] for condition in self.condition_names]
        f1_scores = [metrics[f'{condition}_f1'] for condition in self.condition_names]
        
        metrics['macro_precision'] = np.mean(precisions)
        metrics['macro_recall'] = np.mean(recalls)
        metrics['macro_f1'] = np.mean(f1_scores)
        
        return metrics


def create_model(model_name: str = 'resnet50', 
                num_conditions: int = 7,
                num_severity_levels: int = 6,
                pretrained: bool = True) -> MultiLabelSkinClassifier:
    """Factory function to create model"""
    return MultiLabelSkinClassifier(
        backbone_name=model_name,
        num_conditions=num_conditions,
        num_severity_levels=num_severity_levels,
        pretrained=pretrained
    )


if __name__ == "__main__":
    # Test model architecture
    print("Testing Model Architecture...")
    
    # Create model
    model = create_model('resnet50')
    
    # Test forward pass
    batch_size = 4
    test_input = torch.randn(batch_size, 3, 224, 224)
    
    with torch.no_grad():
        outputs = model(test_input)
    
    print(f"Input shape: {test_input.shape}")
    print(f"Condition logits shape: {outputs['condition_logits'].shape}")
    print(f"Severity logits shape: {outputs['severity_logits'].shape}")
    print(f"Features shape: {outputs['features'].shape}")
    
    # Test loss function
    criterion = CombinedLoss()
    condition_targets = torch.randint(0, 2, (batch_size, 7)).float()
    severity_targets = torch.randint(-1, 6, (batch_size, 7))
    
    loss_dict = criterion(
        outputs['condition_logits'],
        outputs['severity_logits'],
        condition_targets,
        severity_targets
    )
    
    print(f"\nLoss components:")
    for key, value in loss_dict.items():
        print(f"  {key}: {value.item():.4f}")
    
    print("Model architecture test completed successfully!")
