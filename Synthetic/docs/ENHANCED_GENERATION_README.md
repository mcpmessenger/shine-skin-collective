# Enhanced Synthetic Skin Image Generation

This enhanced script generates diverse synthetic skin images for training ML models to classify 6 skin conditions across 3 severity levels.

## Key Features

### 🎯 **10 Images Per Condition/Severity**
- Generates 10 diverse faces for each of the 21 condition/severity combinations
- Total: 210 images (7 conditions × 3 severities × 10 images)

### 🌍 **Demographic Diversity**
- **Age Groups**: Young adult (18-25), Adult (26-40), Middle-aged (41-60), Senior (60+), Elderly (70+)
- **Skin Tones**: 8 different skin tone variations from very fair to dark
- **Gender**: Male, female, non-binary representation

### 🔍 **Face Detection Optimized**
- **Proper Framing**: Full face visible from chin to forehead with shoulders included
- **Optimal Distance**: Not too close (avoiding detection issues) or too far
- **Consistent Composition**: Centered, eye-level camera angle for reliable face detection
- **High Quality**: Sharp focus on facial features suitable for ML preprocessing

### 📊 **Training-Ready Metadata**
Each image includes comprehensive metadata for ML training:

#### Classification Targets
```json
{
  "classification_targets": {
    "acne": true,
    "fine_lines_wrinkles": false,
    "aging": false,
    "hyperpigmentation": false,
    "textured_skin": false,
    "redness": false,
    "pore_size": false
  }
}
```

#### Severity Targets
```json
{
  "severity_targets": {
    "acne": "moderate",
    "fine_lines_wrinkles": "none",
    "aging": "none",
    "hyperpigmentation": "none",
    "textured_skin": "none",
    "redness": "none",
    "pore_size": "none"
  }
}
```

#### Demographics
```json
{
  "demographics": {
    "age_group": "adult",
    "age_range": "26-40",
    "skin_tone": "medium skin tone",
    "gender": "female",
    "variation_index": 3
  }
}
```

## Usage

### Basic Usage
```bash
python generate_skin_images_enhanced.py
```

### Custom Configuration
```bash
# Generate 5 images per condition/severity
export IMAGES_PER_CONDITION=5

# Use custom output directory
export OUTPUT_DIR="./my_dataset"

# Reduce delay between API calls (be careful with rate limits)
export GENERATION_DELAY_SECONDS=15

python generate_skin_images_enhanced.py
```

### Test Run
```bash
# Generate only 2 images per condition/severity for testing
python test_generation.py
```

## Output Structure

```
output_images/
├── dataset_summary_20241201_143022.json
├── acne/
│   ├── mild/
│   │   ├── acne_mild_20241201_143022_0000.png
│   │   ├── acne_mild_20241201_143022_0000.json
│   │   └── ...
│   ├── moderate/
│   └── severe/
├── fine_lines_wrinkles/
│   ├── mild/
│   ├── moderate/
│   └── severe/
└── ... (other conditions)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Google API key for Gemini |
| `IMAGES_PER_CONDITION` | 10 | Number of images per condition/severity |
| `OUTPUT_DIR` | `./output_images` | Output directory |
| `GENERATION_DELAY_SECONDS` | 30 | Delay between API calls |
| `GEMINI_IMAGE_MODEL` | `models/gemini-2.0-flash-preview-image-generation` | Model to use |

## Dataset Summary

After generation, a `dataset_summary_TIMESTAMP.json` file is created with:
- Total images generated
- Generation timestamp
- Conditions covered
- Expected vs actual counts

## Training Integration

The generated metadata is structured for easy integration with ML training pipelines:

1. **Multi-label Classification**: Use `classification_targets` for training
2. **Severity Prediction**: Use `severity_targets` for training
3. **Demographic Analysis**: Use `demographics` for bias analysis
4. **Quality Control**: Use `quality_metrics` for filtering

## Next Steps

1. **Expert Annotation**: Have dermatologists review and validate the synthetic images
2. **Real Data Collection**: Collect real-world selfie images with similar metadata
3. **Model Training**: Use this data to train the 6-category classification model
4. **Continuous Improvement**: Iterate based on model performance and expert feedback

---

## Developer Information

**Developed by:** [@sentilabs01](https://github.com/sentilabs01/shine-skincare-app)  
**Website:** [shineskincollective.com](https://shineskincollective.com)

This enhanced synthetic data generation tool is part of the Shine Skincare App project, designed to create diverse, training-ready datasets for AI-powered skin condition analysis.
