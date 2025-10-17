"""
Training Script for Shine Skin Collective ML Model
Multi-label skin condition classification with severity prediction
"""

import os
import json
import time
import argparse
from typing import Dict, List, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from sklearn.metrics import classification_report, multilabel_confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import wandb
from datetime import datetime

# Import our custom modules
from data_pipeline import SkinDataLoader, SkinConditionDataset
from model_architecture import (
    MultiLabelSkinClassifier, 
    CombinedLoss, 
    ModelMetrics,
    create_model
)


class SkinConditionTrainer:
    """Main training class for skin condition classification"""
    
    def __init__(self, 
                 model_name: str = 'resnet50',
                 batch_size: int = 32,
                 learning_rate: float = 1e-4,
                 num_epochs: int = 100,
                 image_size: int = 224,
                 device: str = 'auto',
                 use_wandb: bool = False,
                 experiment_name: Optional[str] = None):
        
        self.model_name = model_name
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.image_size = image_size
        self.use_wandb = use_wandb
        
        # Set device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        
        # Initialize experiment tracking
        if use_wandb:
            self.experiment_name = experiment_name or f"skin_classifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            wandb.init(
                project="shine-skin-collective",
                name=self.experiment_name,
                config={
                    'model_name': model_name,
                    'batch_size': batch_size,
                    'learning_rate': learning_rate,
                    'num_epochs': num_epochs,
                    'image_size': image_size,
                    'device': str(self.device)
                }
            )
        
        # Initialize components
        self.data_loader = SkinDataLoader()
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        self.metrics = None
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.train_metrics = []
        self.val_metrics = []
        
        # Best model tracking
        self.best_val_f1 = 0.0
        self.best_model_state = None
    
    def setup_model(self):
        """Initialize model, optimizer, scheduler, and loss function"""
        print("Setting up model...")
        
        # Create model
        self.model = create_model(
            model_name=self.model_name,
            num_conditions=7,
            num_severity_levels=6,
            pretrained=True
        ).to(self.device)
        
        # Initialize optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=1e-4
        )
        
        # Initialize scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            T_max=self.num_epochs,
            eta_min=1e-6
        )
        
        # Initialize loss function
        self.criterion = CombinedLoss(
            condition_weight=1.0,
            severity_weight=0.5,
            use_focal_loss=True
        )
        
        # Initialize metrics
        self.metrics = ModelMetrics(num_conditions=7)
        
        print(f"Model setup complete. Total parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def setup_data(self):
        """Setup data loaders"""
        print("Setting up data loaders...")
        
        self.train_loader, self.val_loader, self.test_loader = self.data_loader.create_data_loaders(
            batch_size=self.batch_size,
            train_split=0.7,
            val_split=0.15,
            image_size=self.image_size
        )
        
        print(f"Data loaders created:")
        print(f"  Train: {len(self.train_loader)} batches")
        print(f"  Val: {len(self.val_loader)} batches")
        print(f"  Test: {len(self.test_loader)} batches")
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        self.metrics.reset()
        
        total_loss = 0.0
        num_batches = len(self.train_loader)
        
        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch+1}/{self.num_epochs} [Train]")
        
        for batch_idx, batch in enumerate(pbar):
            # Move to device
            images = batch['image'].to(self.device)
            condition_targets = batch['condition_targets'].to(self.device)
            severity_targets = batch['severity_targets'].to(self.device)
            
            # Forward pass
            outputs = self.model(images)
            
            # Compute loss
            loss_dict = self.criterion(
                outputs['condition_logits'],
                outputs['severity_logits'],
                condition_targets,
                severity_targets
            )
            
            loss = loss_dict['total_loss']
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            # Update metrics
            total_loss += loss.item()
            self.metrics.update(
                outputs['condition_logits'],
                outputs['severity_logits'],
                condition_targets,
                severity_targets
            )
            
            # Update progress bar
            pbar.set_postfix({
                'Loss': f"{loss.item():.4f}",
                'Avg Loss': f"{total_loss/(batch_idx+1):.4f}"
            })
            
            # Log to wandb
            if self.use_wandb and batch_idx % 10 == 0:
                wandb.log({
                    'train/batch_loss': loss.item(),
                    'train/condition_loss': loss_dict['condition_loss'].item(),
                    'train/severity_loss': loss_dict['severity_loss'].item(),
                    'epoch': epoch,
                    'batch': batch_idx
                })
        
        # Compute epoch metrics
        epoch_loss = total_loss / num_batches
        epoch_metrics = self.metrics.compute_metrics()
        
        return {
            'loss': epoch_loss,
            **epoch_metrics
        }
    
    def validate_epoch(self, epoch: int) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        self.metrics.reset()
        
        total_loss = 0.0
        num_batches = len(self.val_loader)
        
        with torch.no_grad():
            pbar = tqdm(self.val_loader, desc=f"Epoch {epoch+1}/{self.num_epochs} [Val]")
            
            for batch_idx, batch in enumerate(pbar):
                # Move to device
                images = batch['image'].to(self.device)
                condition_targets = batch['condition_targets'].to(self.device)
                severity_targets = batch['severity_targets'].to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                
                # Compute loss
                loss_dict = self.criterion(
                    outputs['condition_logits'],
                    outputs['severity_logits'],
                    condition_targets,
                    severity_targets
                )
                
                loss = loss_dict['total_loss']
                total_loss += loss.item()
                
                # Update metrics
                self.metrics.update(
                    outputs['condition_logits'],
                    outputs['severity_logits'],
                    condition_targets,
                    severity_targets
                )
                
                # Update progress bar
                pbar.set_postfix({
                    'Loss': f"{loss.item():.4f}",
                    'Avg Loss': f"{total_loss/(batch_idx+1):.4f}"
                })
        
        # Compute epoch metrics
        epoch_loss = total_loss / num_batches
        epoch_metrics = self.metrics.compute_metrics()
        
        return {
            'loss': epoch_loss,
            **epoch_metrics
        }
    
    def save_checkpoint(self, epoch: int, is_best: bool = False):
        """Save model checkpoint"""
        checkpoint_dir = "checkpoints"
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics,
            'best_val_f1': self.best_val_f1,
            'config': {
                'model_name': self.model_name,
                'batch_size': self.batch_size,
                'learning_rate': self.learning_rate,
                'image_size': self.image_size
            }
        }
        
        # Save regular checkpoint
        checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_epoch_{epoch+1}.pth")
        torch.save(checkpoint, checkpoint_path)
        
        # Save best model
        if is_best:
            best_path = os.path.join(checkpoint_dir, "best_model.pth")
            torch.save(checkpoint, best_path)
            print(f"New best model saved! Val F1: {self.best_val_f1:.4f}")
    
    def plot_training_history(self):
        """Plot training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        epochs = range(1, len(self.train_losses) + 1)
        
        # Loss plot
        axes[0, 0].plot(epochs, self.train_losses, label='Train Loss')
        axes[0, 0].plot(epochs, self.val_losses, label='Val Loss')
        axes[0, 0].set_title('Training and Validation Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # F1 Score plot
        train_f1 = [m['macro_f1'] for m in self.train_metrics]
        val_f1 = [m['macro_f1'] for m in self.val_metrics]
        axes[0, 1].plot(epochs, train_f1, label='Train F1')
        axes[0, 1].plot(epochs, val_f1, label='Val F1')
        axes[0, 1].set_title('Macro F1 Score')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('F1 Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Accuracy plot
        train_acc = [m['accuracy'] for m in self.train_metrics]
        val_acc = [m['accuracy'] for m in self.val_metrics]
        axes[1, 0].plot(epochs, train_acc, label='Train Acc')
        axes[1, 0].plot(epochs, val_acc, label='Val Acc')
        axes[1, 0].set_title('Accuracy')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Accuracy')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Learning rate plot
        lr_values = [self.scheduler.get_last_lr()[0] for _ in epochs]
        axes[1, 1].plot(epochs, lr_values)
        axes[1, 1].set_title('Learning Rate')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Learning Rate')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def train(self):
        """Main training loop"""
        print("Starting training...")
        print(f"Model: {self.model_name}")
        print(f"Batch size: {self.batch_size}")
        print(f"Learning rate: {self.learning_rate}")
        print(f"Epochs: {self.num_epochs}")
        print(f"Device: {self.device}")
        
        start_time = time.time()
        
        for epoch in range(self.num_epochs):
            print(f"\n{'='*50}")
            print(f"Epoch {epoch+1}/{self.num_epochs}")
            print(f"{'='*50}")
            
            # Train
            train_metrics = self.train_epoch(epoch)
            self.train_losses.append(train_metrics['loss'])
            self.train_metrics.append(train_metrics)
            
            # Validate
            val_metrics = self.validate_epoch(epoch)
            self.val_losses.append(val_metrics['loss'])
            self.val_metrics.append(val_metrics)
            
            # Update scheduler
            self.scheduler.step()
            
            # Print epoch results
            print(f"Train Loss: {train_metrics['loss']:.4f}, Val Loss: {val_metrics['loss']:.4f}")
            print(f"Train F1: {train_metrics['macro_f1']:.4f}, Val F1: {val_metrics['macro_f1']:.4f}")
            print(f"Train Acc: {train_metrics['accuracy']:.4f}, Val Acc: {val_metrics['accuracy']:.4f}")
            
            # Check if best model
            is_best = val_metrics['macro_f1'] > self.best_val_f1
            if is_best:
                self.best_val_f1 = val_metrics['macro_f1']
                self.best_model_state = self.model.state_dict().copy()
            
            # Save checkpoint
            if (epoch + 1) % 10 == 0 or is_best:
                self.save_checkpoint(epoch, is_best)
            
            # Log to wandb
            if self.use_wandb:
                wandb.log({
                    'epoch': epoch,
                    'train/loss': train_metrics['loss'],
                    'train/f1': train_metrics['macro_f1'],
                    'train/accuracy': train_metrics['accuracy'],
                    'val/loss': val_metrics['loss'],
                    'val/f1': val_metrics['macro_f1'],
                    'val/accuracy': val_metrics['accuracy'],
                    'lr': self.scheduler.get_last_lr()[0]
                })
            
            # Early stopping check
            if epoch > 20 and val_metrics['macro_f1'] < 0.3:
                print("Early stopping triggered - validation F1 too low")
                break
        
        training_time = time.time() - start_time
        print(f"\nTraining completed in {training_time/3600:.2f} hours")
        print(f"Best validation F1: {self.best_val_f1:.4f}")
        
        # Plot training history
        self.plot_training_history()
        
        # Save final model
        self.save_checkpoint(self.num_epochs - 1)
        
        if self.use_wandb:
            wandb.finish()


def main():
    parser = argparse.ArgumentParser(description='Train Skin Condition Classifier')
    parser.add_argument('--model', type=str, default='resnet50', 
                       help='Model architecture (resnet50, efficientnet-b0, etc.)')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--image-size', type=int, default=224, help='Input image size')
    parser.add_argument('--device', type=str, default='auto', help='Device (auto, cpu, cuda)')
    parser.add_argument('--wandb', action='store_true', help='Use Weights & Biases logging')
    parser.add_argument('--experiment-name', type=str, default=None, help='Experiment name for wandb')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = SkinConditionTrainer(
        model_name=args.model,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        num_epochs=args.epochs,
        image_size=args.image_size,
        device=args.device,
        use_wandb=args.wandb,
        experiment_name=args.experiment_name
    )
    
    # Setup and train
    trainer.setup_data()
    trainer.setup_model()
    trainer.train()


if __name__ == "__main__":
    main()
