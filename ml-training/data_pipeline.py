"""
Data Pipeline for Shine Skin Collective ML Training
Handles loading, preprocessing, and augmentation of synthetic skin images
"""

import os
import json
import numpy as np
import pandas as pd
from PIL import Image
import cv2
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
import albumentations as A
from albumentations.pytorch import ToTensorV2
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms


class SkinConditionDataset(Dataset):
    """Custom Dataset for skin condition images with multi-label classification"""
    
    def __init__(self, image_paths: List[str], labels: List[Dict], 
                 transforms: Optional[A.Compose] = None, 
                 severity_labels: Optional[List[Dict]] = None):
        self.image_paths = image_paths
        self.labels = labels
        self.severity_labels = severity_labels
        self.transforms = transforms
        
        # Define the 7 skin conditions we're classifying
        self.condition_names = [
            'acne', 'aging', 'fine_lines_wrinkles', 'hyperpigmentation',
            'pore_size', 'redness', 'textured_skin'
        ]
        
        # Define severity levels
        self.severity_levels = [
            'slight', 'mild', 'moderate', 'severe', 'advanced', 'early_signs'
        ]
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # Load image
        image_path = self.image_paths[idx]
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Load labels
        label_dict = self.labels[idx]
        
        # Create multi-label classification targets
        condition_targets = []
        for condition in self.condition_names:
            condition_targets.append(label_dict.get(condition, {}).get('present', False))
        
        # Create severity targets (only for present conditions)
        severity_targets = []
        for condition in self.condition_names:
            if condition_targets[len(severity_targets)]:
                severity = label_dict.get(condition, {}).get('severity_level', 'mild')
                severity_targets.append(self.severity_levels.index(severity) if severity in self.severity_levels else 0)
            else:
                severity_targets.append(-1)  # No severity for absent conditions
        
        # Apply transforms
        if self.transforms:
            transformed = self.transforms(image=image)
            image = transformed['image']
        
        return {
            'image': image,
            'condition_targets': torch.tensor(condition_targets, dtype=torch.float32),
            'severity_targets': torch.tensor(severity_targets, dtype=torch.long),
            'image_path': image_path,
            'original_labels': label_dict
        }


class SkinDataLoader:
    """Data loader class for handling synthetic skin dataset"""
    
    def __init__(self, data_root: Optional[str] = None):
        # Resolve dataset path relative to the repository root by default
        if data_root is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.data_root = os.path.join(base_dir, 'Synthetic', 'output_images')
        else:
            self.data_root = data_root
        self.condition_names = [
            'acne', 'aging', 'fine_lines_wrinkles', 'hyperpigmentation',
            'pore_size', 'redness', 'textured_skin'
        ]
        self.severity_levels = [
            'slight', 'mild', 'moderate', 'severe', 'advanced', 'early_signs'
        ]
    
    def load_dataset(self) -> Tuple[List[str], List[Dict], List[Dict]]:
        """Load all images and their annotations from the synthetic dataset"""
        image_paths = []
        labels = []
        severity_labels = []
        
        # Walk through all condition directories
        for condition_dir in os.listdir(self.data_root):
            condition_path = os.path.join(self.data_root, condition_dir)
            if not os.path.isdir(condition_path):
                continue
                
            # Skip summary files
            if condition_dir.endswith('.json') or condition_dir.endswith('.md'):
                continue
            
            print(f"Loading data from {condition_dir}...")
            
            # Walk through severity subdirectories
            for severity_dir in os.listdir(condition_path):
                severity_path = os.path.join(condition_path, severity_dir)
                if not os.path.isdir(severity_path):
                    continue
                
                # Load all images and their JSON annotations
                for filename in os.listdir(severity_path):
                    if filename.endswith('.png'):
                        image_path = os.path.join(severity_path, filename)
                        json_path = os.path.join(severity_path, filename.replace('.png', '.json'))
                        
                        if os.path.exists(json_path):
                            # Load JSON annotation
                            with open(json_path, 'r') as f:
                                annotation = json.load(f)
                            
                            # Extract classification targets
                            classification_targets = annotation.get('classification_targets', {})
                            severity_targets = annotation.get('severity_targets', {})
                            
                            # Create label dictionary for this image
                            label_dict = {}
                            for condition in self.condition_names:
                                present = classification_targets.get(condition, False)
                                severity = severity_targets.get(condition, 'mild')
                                
                                label_dict[condition] = {
                                    'present': present,
                                    'severity_level': severity,
                                    'confidence': annotation.get('training_annotations', {}).get('confidence_score', 0.5)
                                }
                            
                            image_paths.append(image_path)
                            labels.append(label_dict)
                            severity_labels.append(severity_targets)
        
        print(f"Loaded {len(image_paths)} images from synthetic dataset")
        return image_paths, labels, severity_labels
    
    def get_train_transforms(self, image_size: int = 224) -> A.Compose:
        """Get training data augmentation transforms"""
        return A.Compose([
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.RandomRotate90(p=0.3),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.1,
                rotate_limit=15,
                p=0.5
            ),
            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.5
            ),
            A.HueSaturationValue(
                hue_shift_limit=20,
                sat_shift_limit=30,
                val_shift_limit=20,
                p=0.5
            ),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    
    def get_val_transforms(self, image_size: int = 224) -> A.Compose:
        """Get validation data transforms (no augmentation)"""
        return A.Compose([
            A.Resize(image_size, image_size),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    
    def create_data_loaders(self, batch_size: int = 32, 
                           train_split: float = 0.7,
                           val_split: float = 0.15,
                           image_size: int = 224) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Create train, validation, and test data loaders"""
        
        # Load dataset
        image_paths, labels, severity_labels = self.load_dataset()
        
        # Split data
        train_paths, temp_paths, train_labels, temp_labels = train_test_split(
            image_paths, labels, test_size=(1-train_split), random_state=42
        )
        
        val_paths, test_paths, val_labels, test_labels = train_test_split(
            temp_paths, temp_labels, 
            test_size=(1-val_split/(1-train_split)), random_state=42
        )
        
        print(f"Train: {len(train_paths)}, Val: {len(val_paths)}, Test: {len(test_paths)}")
        
        # Create datasets
        train_dataset = SkinConditionDataset(
            train_paths, train_labels, 
            transforms=self.get_train_transforms(image_size)
        )
        
        val_dataset = SkinConditionDataset(
            val_paths, val_labels,
            transforms=self.get_val_transforms(image_size)
        )
        
        test_dataset = SkinConditionDataset(
            test_paths, test_labels,
            transforms=self.get_val_transforms(image_size)
        )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True, num_workers=4
        )
        
        val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False, num_workers=4
        )
        
        test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False, num_workers=4
        )
        
        return train_loader, val_loader, test_loader


def analyze_dataset_distribution(data_loader: DataLoader) -> Dict:
    """Analyze the distribution of conditions in the dataset"""
    condition_counts = {name: 0 for name in [
        'acne', 'aging', 'fine_lines_wrinkles', 'hyperpigmentation',
        'pore_size', 'redness', 'textured_skin'
    ]}
    
    severity_counts = {level: 0 for level in [
        'slight', 'mild', 'moderate', 'severe', 'advanced', 'early_signs'
    ]}
    
    total_samples = 0
    
    for batch in data_loader:
        condition_targets = batch['condition_targets']
        severity_targets = batch['severity_targets']
        
        total_samples += condition_targets.size(0)
        
        # Count conditions
        for i, condition in enumerate(condition_counts.keys()):
            condition_counts[condition] += condition_targets[:, i].sum().item()
        
        # Count severities
        for batch_idx in range(severity_targets.size(0)):
            for condition_idx in range(severity_targets.size(1)):
                severity_idx = severity_targets[batch_idx, condition_idx].item()
                if severity_idx >= 0:  # Valid severity
                    severity_counts[list(severity_counts.keys())[severity_idx]] += 1
    
    # Calculate percentages
    condition_percentages = {
        condition: (count / total_samples) * 100 
        for condition, count in condition_counts.items()
    }
    
    return {
        'total_samples': total_samples,
        'condition_counts': condition_counts,
        'condition_percentages': condition_percentages,
        'severity_counts': severity_counts
    }


if __name__ == "__main__":
    # Test the data pipeline
    print("Testing Skin Data Pipeline...")
    
    loader = SkinDataLoader()
    train_loader, val_loader, test_loader = loader.create_data_loaders(batch_size=16)
    
    # Analyze dataset distribution
    print("\nDataset Analysis:")
    train_dist = analyze_dataset_distribution(train_loader)
    print(f"Total training samples: {train_dist['total_samples']}")
    print("\nCondition distribution:")
    for condition, percentage in train_dist['condition_percentages'].items():
        print(f"  {condition}: {percentage:.2f}%")
    
    # Test loading a batch
    print("\nTesting batch loading...")
    for batch in train_loader:
        print(f"Batch shape: {batch['image'].shape}")
        print(f"Condition targets shape: {batch['condition_targets'].shape}")
        print(f"Severity targets shape: {batch['severity_targets'].shape}")
        break
    
    print("Data pipeline test completed successfully!")
