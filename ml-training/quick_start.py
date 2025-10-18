"""
Quick Start Script for Shine Skin Collective ML Training
This script provides an easy way to start training with sensible defaults
"""

import os
import sys
import argparse
import torch
from train import SkinConditionTrainer


def check_environment():
    """Check if the environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check PyTorch
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        # Check CUDA availability
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("⚠️  CUDA not available, will use CPU")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    # Check other dependencies
    required_packages = ['numpy', 'pandas', 'sklearn', 'matplotlib', 'albumentations', 'timm']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            return False
    
    # Check data directory (resolve relative to repo root)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_path = os.path.join(base_dir, 'Synthetic', 'output_images')
    if os.path.exists(data_path):
        print(f"✅ Synthetic dataset found at {data_path}")
        
        # Count images
        image_count = 0
        for root, dirs, files in os.walk(data_path):
            image_count += len([f for f in files if f.endswith('.png')])
        print(f"   Found {image_count} images")
    else:
        print(f"❌ Synthetic dataset not found at {data_path}")
        return False
    
    return True


def run_quick_training():
    """Run training with quick start defaults"""
    print("\n🚀 Starting Quick Training Session...")
    print("=" * 50)
    
    # Quick training configuration
    config = {
        'model_name': 'resnet50',
        'batch_size': 16,  # Smaller batch size for quick training
        'learning_rate': 1e-4,
        'num_epochs': 5,   # Just 5 epochs for quick test
        'image_size': 224,
        'device': 'auto',
        'use_wandb': False
    }
    
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Create trainer
    trainer = SkinConditionTrainer(**config)
    
    # Setup and train
    trainer.setup_data()
    trainer.setup_model()
    trainer.train()
    
    print("\n✅ Quick training completed!")
    print("Check the 'checkpoints' directory for saved models")
    print("Check 'training_history.png' for training plots")


def run_full_training():
    """Run full training with production settings"""
    print("\n🔥 Starting Full Training Session...")
    print("=" * 50)
    
    # Production training configuration
    config = {
        'model_name': 'resnet50',
        'batch_size': 32,
        'learning_rate': 1e-4,
        'num_epochs': 100,
        'image_size': 224,
        'device': 'auto',
        'use_wandb': False,  # Set to True if you want to use Weights & Biases
        'experiment_name': 'skin_classifier_full_training'
    }
    
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Create trainer
    trainer = SkinConditionTrainer(**config)
    
    # Setup and train
    trainer.setup_data()
    trainer.setup_model()
    trainer.train()
    
    print("\n✅ Full training completed!")
    print("Check the 'checkpoints' directory for saved models")
    print("Check 'training_history.png' for training plots")


def run_evaluation():
    """Run evaluation on test set"""
    print("\n📊 Running Model Evaluation...")
    print("=" * 50)
    
    # This would load the best model and evaluate on test set
    # Implementation would go here
    print("Evaluation functionality coming soon!")
    print("For now, you can use the trained model for inference")


def main():
    parser = argparse.ArgumentParser(description='Quick Start for Skin Condition ML Training')
    parser.add_argument('--mode', type=str, default='check',
                       choices=['check', 'quick', 'full', 'eval'],
                       help='Mode to run: check environment, quick training, full training, or evaluation')
    parser.add_argument('--gpu', action='store_true', help='Force GPU usage')
    parser.add_argument('--wandb', action='store_true', help='Enable Weights & Biases logging')
    
    args = parser.parse_args()
    
    print("🌟 Shine Skin Collective - ML Training Quick Start")
    print("=" * 60)
    
    if args.mode == 'check':
        if check_environment():
            print("\n✅ Environment check passed! Ready for training.")
            print("\nNext steps:")
            print("  python quick_start.py --mode quick    # Quick 5-epoch test")
            print("  python quick_start.py --mode full     # Full 100-epoch training")
        else:
            print("\n❌ Environment check failed. Please fix the issues above.")
            return
    
    elif args.mode == 'quick':
        if not check_environment():
            print("\n❌ Environment check failed. Please fix the issues first.")
            return
        run_quick_training()
    
    elif args.mode == 'full':
        if not check_environment():
            print("\n❌ Environment check failed. Please fix the issues first.")
            return
        
        # Confirm with user
        print("\n⚠️  Full training will take several hours and use significant computational resources.")
        response = input("Do you want to continue? (y/N): ")
        if response.lower() != 'y':
            print("Training cancelled.")
            return
        
        run_full_training()
    
    elif args.mode == 'eval':
        run_evaluation()
    
    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
