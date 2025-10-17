# ML Training for Shine Skin Collective

This directory contains the complete machine learning training pipeline for the Shine Skin Collective skin condition classification model.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Check environment
python quick_start.py --mode check
```

### 2. Quick Training Test (5 epochs)

```bash
python quick_start.py --mode quick
```

### 3. Full Training (100 epochs)

```bash
python quick_start.py --mode full
```

## 📁 File Structure

```
ml-training/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config.yaml              # Training configuration
├── quick_start.py           # Easy start script
├── data_pipeline.py         # Data loading and preprocessing
├── model_architecture.py    # Model definitions and loss functions
├── train.py                 # Main training script
└── checkpoints/             # Saved models (created during training)
```

## 🏗️ Architecture Overview

### Model Architecture
- **Backbone**: Pre-trained CNN (ResNet50, EfficientNet, ViT)
- **Classification Head**: Multi-label binary classification (7 skin conditions)
- **Severity Head**: Multi-class classification (6 severity levels per condition)

### Supported Models
- ResNet50/101
- EfficientNet-B0/B3
- Vision Transformer (ViT)

### Skin Conditions Classified
1. Acne
2. Aging
3. Fine Lines & Wrinkles
4. Hyperpigmentation
5. Pore Size
6. Redness
7. Textured Skin

### Severity Levels
- Slight
- Mild
- Moderate
- Severe
- Advanced
- Early Signs

## 📊 Training Features

### Data Augmentation
- Horizontal flipping
- Random rotation
- Shift, scale, and rotate
- Brightness and contrast adjustment
- Hue, saturation, and value shifts
- Gaussian noise

### Loss Function
- **Focal Loss**: For handling class imbalance in multi-label classification
- **Combined Loss**: Condition detection + severity prediction
- **Weighted Loss**: Configurable weights for different tasks

### Training Features
- Mixed precision training (optional)
- Gradient clipping
- Learning rate scheduling (Cosine Annealing)
- Early stopping
- Model checkpointing
- Comprehensive metrics tracking

## 🔧 Usage

### Basic Training

```python
from train import SkinConditionTrainer

# Create trainer
trainer = SkinConditionTrainer(
    model_name='resnet50',
    batch_size=32,
    learning_rate=1e-4,
    num_epochs=100
)

# Setup and train
trainer.setup_data()
trainer.setup_model()
trainer.train()
```

### Advanced Training with Custom Config

```python
from train import SkinConditionTrainer

trainer = SkinConditionTrainer(
    model_name='efficientnet-b3',
    batch_size=16,
    learning_rate=5e-5,
    num_epochs=150,
    use_wandb=True,
    experiment_name='efficientnet_experiment'
)

trainer.setup_data()
trainer.setup_model()
trainer.train()
```

### Command Line Training

```bash
# Basic training
python train.py

# Advanced training with custom parameters
python train.py --model efficientnet-b3 --batch-size 16 --lr 5e-5 --epochs 150

# Training with Weights & Biases logging
python train.py --wandb --experiment-name "my_experiment"
```

## 📈 Metrics and Evaluation

### Training Metrics
- **Loss**: Combined loss (condition + severity)
- **Accuracy**: Overall classification accuracy
- **F1 Score**: Macro-averaged F1 score across all conditions
- **Per-Condition Metrics**: Precision, recall, F1 for each condition

### Validation Metrics
- Real-time validation during training
- Best model checkpointing based on validation F1
- Training history visualization

## 💾 Model Saving

Models are automatically saved to the `checkpoints/` directory:

- `checkpoint_epoch_X.pth`: Regular checkpoints
- `best_model.pth`: Best model based on validation F1
- Training history plots saved as `training_history.png`

## 🔍 Monitoring

### Local Monitoring
- Real-time progress bars during training
- Training history plots
- Console output with metrics

### Weights & Biases Integration
```bash
# Enable W&B logging
python train.py --wandb --experiment-name "my_experiment"
```

## 🎯 Performance Targets

- **Classification F1**: > 0.85 (macro average)
- **Per-Condition F1**: > 0.80 for each condition
- **Inference Speed**: < 100ms per image
- **Model Size**: Optimized for deployment

## 🛠️ Customization

### Custom Model Architecture
```python
from model_architecture import MultiLabelSkinClassifier

# Create custom model
model = MultiLabelSkinClassifier(
    backbone_name='resnet101',
    num_conditions=7,
    num_severity_levels=6,
    dropout_rate=0.5
)
```

### Custom Loss Function
```python
from model_architecture import CombinedLoss

# Custom loss weights
criterion = CombinedLoss(
    condition_weight=1.0,
    severity_weight=0.3,
    use_focal_loss=True
)
```

### Custom Data Augmentation
```python
from data_pipeline import SkinDataLoader

loader = SkinDataLoader()

# Custom transforms
custom_transforms = loader.get_train_transforms(image_size=256)
# Modify transforms as needed
```

## 🐛 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size: `--batch-size 16`
   - Use smaller model: `--model resnet50`

2. **Slow Training**
   - Increase batch size if memory allows
   - Use mixed precision training
   - Ensure GPU is being used

3. **Poor Performance**
   - Check data quality and distribution
   - Adjust learning rate
   - Try different model architectures
   - Increase training epochs

### Debug Mode
```bash
# Run with smaller dataset for debugging
python train.py --epochs 2 --batch-size 8
```

## 📚 Next Steps

1. **Model Optimization**: Try different architectures and hyperparameters
2. **Data Augmentation**: Experiment with additional augmentation techniques
3. **Ensemble Methods**: Combine multiple models for better performance
4. **Model Deployment**: Convert trained model for production use
5. **API Integration**: Integrate model with the Next.js application

## 🤝 Contributing

When contributing to the ML training code:

1. Follow the existing code style
2. Add comprehensive docstrings
3. Include type hints
4. Test with small datasets first
5. Update documentation as needed

## 📞 Support

For issues with ML training:

1. Check the troubleshooting section above
2. Review the training logs
3. Verify data quality and format
4. Check GPU/CUDA setup if using GPU training
