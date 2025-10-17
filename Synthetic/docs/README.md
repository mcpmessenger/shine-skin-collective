# Shine Synthetic Face Dataset

A comprehensive synthetic skin condition dataset with AI-generated images, dermatologist annotation tools, and training-ready metadata for machine learning applications.

## Overview

This project provides a complete pipeline for creating and curating synthetic skin condition datasets. It includes:
- **AI-generated images** using Google's Gemini 2.0 Flash model
- **Dermatologist annotation tools** for expert validation and curation
- **Training-ready metadata** with comprehensive JSON annotations
- **Quality control workflows** for dataset refinement

## 🎯 Key Features

### **Complete Dataset Pipeline**
- **✅ Generated Dataset**: 210 images across 7 conditions × 3 severities × 10 images each
- **✅ Dermatologist Tools**: Web-based annotation interface for expert validation
- **✅ Quality Control**: Batch relabeling and curation workflows
- **✅ Training-Ready**: Comprehensive metadata for ML model development

### **Data Generation Capabilities**
- **10 Images Per Condition/Severity**: Diverse faces for each condition/severity combination
- **Demographic Diversity**: Age groups, skin tones, and gender variations
- **Face Detection Optimized**: Proper framing and composition for ML preprocessing
- **High Quality**: Sharp focus on facial features suitable for analysis

### **7 Skin Condition Categories**
- **Acne** (mild/moderate/severe)
- **Fine Lines & Wrinkles** (mild/moderate/severe)
- **Aging** (early_signs/moderate/advanced)
- **Hyperpigmentation** (mild/moderate/severe)
- **Textured Skin** (slight/moderate/severe)
- **Redness** (mild/moderate/severe)
- **Pore Size** (mild/moderate/severe)
- **Healthy** (clear_skin/minimal_concerns/well_maintained)

### **Advanced Metadata Structure**
Each image includes comprehensive metadata for ML training:
- **Multi-label Classification Targets**: Boolean flags for all 7 conditions
- **Severity Targets**: Specific severity level for each condition
- **Demographics**: Age group, skin tone, gender information
- **Quality Metrics**: Image resolution, lighting, pose quality
- **Training Annotations**: Confidence scores, affected percentages, feature counts
- **Expert Validation**: Dermatologist review and curation tracking

## 📁 Generated Dataset Structure

```
output_images/
├── dataset_summary_TIMESTAMP.json
├── acne/
│   ├── mild/
│   │   ├── acne_mild_TIMESTAMP_0000.png
│   │   ├── acne_mild_TIMESTAMP_0000.json
│   │   └── ... (10 images total)
│   ├── moderate/
│   └── severe/
├── fine_lines_wrinkles/
├── aging/
├── hyperpigmentation/
├── textured_skin/
├── redness/
└── pore_size/
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API key with Gemini access (for generation)
- Modern web browser (for dermatologist tools)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/sentilabs01/shine-skincare-app.git
cd shine-skincare-app/Synthetic\ Face\ Dataset
```

2. **Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies:**
```bash
pip install -U google-generativeai pillow requests flask
```

4. **Set environment variables:**
```bash
# Required for generation
set GOOGLE_API_KEY=your_api_key_here

# Optional
set IMAGES_PER_CONDITION=10
set OUTPUT_DIR=./output_images
set GENERATION_DELAY_SECONDS=30
```

### Usage

#### **1. Generate Synthetic Dataset**
```bash
# Generate full dataset (210 images)
python generate_skin_images_enhanced.py

# Test generation (42 images)
python test_generation.py
```

#### **2. Dermatologist Annotation & Curation**
```bash
# Start the web-based annotation tool
start_swipe_tool.bat          # Windows
# or
.\start_swipe_tool.ps1        # PowerShell

# Command-line relabeling tool
python relabel_api.py
```

#### **3. Custom Configuration**
```bash
# Generate 5 images per condition/severity
export IMAGES_PER_CONDITION=5

# Use custom output directory
export OUTPUT_DIR="./my_dataset"

# Reduce delay between API calls
export GENERATION_DELAY_SECONDS=15

python generate_skin_images_enhanced.py
```

## 📊 Metadata Format

Each image is paired with a comprehensive JSON annotation file:

```json
{
    "image_filename": "acne_mild_20250910_162703_0000.png",
    "skin_condition": "acne",
    "severity": "mild",
    "classification_targets": {
        "acne": true,
        "fine_lines_wrinkles": false,
        "aging": false,
        "hyperpigmentation": false,
        "textured_skin": false,
        "redness": false,
        "pore_size": false
    },
    "severity_targets": {
        "acne": "mild",
        "fine_lines_wrinkles": "none",
        "aging": "none",
        "hyperpigmentation": "none",
        "textured_skin": "none",
        "redness": "none",
        "pore_size": "none"
    },
    "demographics": {
        "age_group": "young_adult",
        "age_range": "18-25",
        "skin_tone": "very fair skin tone",
        "gender": "male"
    },
    "training_annotations": {
        "condition_detected": true,
        "severity_level": "mild",
        "confidence_score": 0.8,
        "affected_percentage": 0.05,
        "feature_count": 5
    }
}
```

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Google API key for Gemini |
| `IMAGES_PER_CONDITION` | 10 | Number of images per condition/severity |
| `OUTPUT_DIR` | `./output_images` | Output directory |
| `GENERATION_DELAY_SECONDS` | 30 | Delay between API calls |
| `GEMINI_IMAGE_MODEL` | `models/gemini-2.0-flash-preview-image-generation` | Model to use |

## 💰 Cost Estimation

- **Images per full run**: 210 (7 conditions × 3 severities × 10 images)
- **Cost per image**: ~$0.03 (Google Gemini pricing)
- **Total cost per run**: ~$6.30
- **Test run cost**: ~$1.26 (42 images)
- **Current dataset**: ✅ 210 images generated and ready for annotation

## 📈 Training Integration

The generated metadata is structured for easy integration with ML training pipelines:

1. **Multi-label Classification**: Use `classification_targets` for training
2. **Severity Prediction**: Use `severity_targets` for training
3. **Demographic Analysis**: Use `demographics` for bias analysis
4. **Quality Control**: Use `quality_metrics` for filtering
5. **Expert Validation**: Use dermatologist annotations for ground truth

## 🎯 Current Project Status

### **✅ Completed**
- **210 synthetic images** generated across 7 conditions
- **Comprehensive metadata** for each image
- **Dermatologist annotation tools** (web interface + CLI)
- **Quality control workflows** for dataset curation
- **Training-ready format** for ML model development

### **🔄 In Progress**
- **Expert validation** of generated images
- **Dataset refinement** based on dermatologist feedback
- **Integration** with Shine Skincare App ML pipeline

### **📋 Next Steps**
1. **Dermatologist Review**: Use annotation tools to validate and refine labels
2. **Quality Control**: Remove poor-quality images and correct misclassifications
3. **Model Training**: Integrate curated dataset with ML training pipeline
4. **Performance Evaluation**: Test model accuracy with synthetic data

## 🔬 Dermatologist Tools

### **Web-Based Annotation Interface**
- **One-at-a-time review** with large, clear images
- **Click-to-categorize** interface for efficient workflow
- **Batch saving** for processing multiple images
- **Quality control** with delete functionality
- **Keyboard shortcuts** for faster operation

### **Command-Line Relabeling Tool**
- **Batch operations** for moving multiple images
- **Automatic metadata updates** when relabeling
- **Path validation** and error prevention
- **Session management** for tracking changes

### **Supported Workflows**
1. **Initial Review**: Load generated images and categorize
2. **Quality Control**: Remove poor-quality or inappropriate images
3. **Expert Validation**: Have dermatologists review and correct labels
4. **Batch Processing**: Efficiently process large datasets

## 📚 Documentation

- **[Enhanced Generation Guide](ENHANCED_GENERATION_README.md)**: Detailed documentation for the enhanced generation script
- **[Dermatologist Tool Guide](DERMATOLOGIST_TOOL_README.md)**: Command-line relabeling tool documentation
- **[Swipe Tool Guide](SWIPE_TOOL_README.md)**: Web-based annotation interface guide
- **[Image Generation Strategy](image_generation_strategy.md)**: Strategic approach to synthetic data generation
- **[ML Architecture Analysis](Restructuring%20App%20and%20ML%20for%20Skin%20Condition%20Analysis%20(1)/)**: Comprehensive analysis and recommendations

## 📋 Summary

This project provides a complete pipeline for creating and curating synthetic skin condition datasets:

1. **✅ Data Generation**: 210 AI-generated images across 7 skin conditions
2. **✅ Expert Tools**: Web-based and CLI tools for dermatologist validation
3. **✅ Quality Control**: Batch processing and curation workflows
4. **✅ Training Ready**: Comprehensive metadata for ML model development

The dataset is ready for dermatologist review and can be integrated directly into ML training pipelines for the Shine Skincare App.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 🆘 Support

For issues and questions, please open an issue on GitHub or contact the maintainers.

---

## Developer Information

**Developed by:** [@sentilabs01](https://github.com/sentilabs01/shine-skincare-app)  
**Website:** [shineskincollective.com](https://shineskincollective.com)

This synthetic data generation and curation tool is part of the Shine Skincare App project, designed to create diverse, expert-validated datasets for AI-powered skin condition analysis.