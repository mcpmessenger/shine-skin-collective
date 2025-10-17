# Synthetic Faces Dataset

A comprehensive synthetic skin condition dataset with AI-generated images, dermatologist annotation tools, and training-ready metadata for machine learning applications.

## 🎯 Overview

This repository contains a complete pipeline for creating and curating synthetic skin condition datasets using AI-generated images. The dataset includes 311+ high-quality synthetic face images across 7 different skin conditions with varying severity levels, designed for machine learning model training and research.

## ✨ Key Features

- **🤖 AI-Generated Images**: High-quality synthetic faces using Google's Gemini 2.0 Flash model
- **👩‍⚕️ Expert Validation Tools**: Web-based dermatologist annotation interface
- **📊 Comprehensive Metadata**: Training-ready JSON annotations for each image
- **🔧 Quality Control**: Batch processing and curation workflows
- **📈 ML-Ready Format**: Structured for easy integration with training pipelines

## 📁 Dataset Structure

```
syntheticfaces/
├── README.md                           # This file
├── output_images/                      # Generated dataset (311+ images)
│   ├── dataset_summary_*.json         # Dataset statistics
│   ├── acne/                          # 7 skin conditions
│   ├── aging/                         # Each with 3 severity levels
│   ├── fine_lines_wrinkles/           # 10+ images per combination
│   ├── hyperpigmentation/
│   ├── pore_size/
│   ├── redness/
│   └── textured_skin/
├── docs/                              # Documentation
│   ├── README.md                      # Main documentation
│   ├── DERMATOLOGIST_TOOL_README.md   # Tool usage guide
│   ├── ENHANCED_GENERATION_README.md  # Generation guide
│   ├── SWIPE_TOOL_README.md          # Web interface guide
│   └── image_generation_strategy.md   # Strategy document
├── scripts/                           # Python scripts
│   ├── generate_skin_images_enhanced.py  # Main generation script
│   ├── relabel_api.py                # CLI relabeling tool
│   ├── changes_server.py             # Change tracking server
│   └── save_changes_api.py           # Save changes API
├── tools/                             # Dermatologist tools
│   ├── dermatologist_drag_drop_tool.html  # Web interface
│   ├── start_dermatologist_server.bat # Windows launcher
│   └── start_full_system.bat         # Full system launcher
└── changes_backup/                    # Backup of changes
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API key with Gemini access (for generation)
- Modern web browser (for dermatologist tools)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/mcpmessenger/syntheticfaces.git
cd syntheticfaces
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
python scripts/generate_skin_images_enhanced.py

# Test generation (42 images)
python scripts/test_generation.py
```

#### **2. Dermatologist Annotation & Curation**
```bash
# Start the web-based annotation tool
tools/start_dermatologist_server.bat          # Windows
# or
python tools/start_dermatologist_server.py   # Python

# Command-line relabeling tool
python scripts/relabel_api.py
```

## 📊 Dataset Statistics

### **Current Dataset (311+ images)**
- **Original Run**: 210 images (complete)
- **Latest Run**: 101+ images (ongoing)
- **Total**: 311+ images across 7 conditions

### **Distribution by Condition**
- **Acne**: 30+ images (mild/moderate/severe)
- **Aging**: 30+ images (early_signs/moderate/advanced)
- **Fine Lines & Wrinkles**: 30+ images (mild/moderate/severe)
- **Hyperpigmentation**: 30+ images (mild/moderate/severe)
- **Pore Size**: 30+ images (mild/moderate/severe)
- **Redness**: 30+ images (mild/moderate/severe)
- **Textured Skin**: 30+ images (slight/moderate/severe)
- **Healthy**: 30+ images (clear_skin/minimal_concerns/well_maintained)

## 🎯 Skin Condition Categories

### **7 Primary Conditions**
1. **Acne** (mild/moderate/severe)
2. **Fine Lines & Wrinkles** (mild/moderate/severe)
3. **Aging** (early_signs/moderate/advanced)
4. **Hyperpigmentation** (mild/moderate/severe)
5. **Textured Skin** (slight/moderate/severe)
6. **Redness** (mild/moderate/severe)
7. **Pore Size** (mild/moderate/severe)

### **Healthy Reference**
- **Clear Skin**: Minimal to no visible concerns
- **Minimal Concerns**: Very minor skin issues
- **Well Maintained**: Good skin with minor age-related changes

## 📋 Metadata Format

Each image includes comprehensive JSON annotations:

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

## 🔧 Configuration

### **Environment Variables**
| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Google API key for Gemini |
| `IMAGES_PER_CONDITION` | 10 | Number of images per condition/severity |
| `OUTPUT_DIR` | `./output_images` | Output directory |
| `GENERATION_DELAY_SECONDS` | 30 | Delay between API calls |
| `GEMINI_IMAGE_MODEL` | `models/gemini-2.0-flash-preview-image-generation` | Model to use |

## 💰 Cost Information

- **Images Generated**: 311+ total
- **Cost per Image**: ~$0.03 (Google Gemini)
- **Total Spent**: ~$9.33+
- **API Quota**: 100 requests per day (free tier)

## 🎯 Use Cases

### **Machine Learning Research**
- **Multi-label Classification**: Train models to detect multiple skin conditions
- **Severity Prediction**: Predict severity levels for each condition
- **Demographic Analysis**: Study bias and fairness in skin analysis
- **Quality Assessment**: Develop image quality metrics

### **Medical Education**
- **Training Materials**: Educational content for dermatology students
- **Case Studies**: Synthetic cases for learning and practice
- **Research**: Studies on skin condition recognition and analysis

### **Industry Applications**
- **Skincare Apps**: Training data for consumer skin analysis apps
- **Telemedicine**: AI-powered preliminary skin condition screening
- **Research Tools**: Datasets for academic and commercial research

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

## 📚 Documentation

- **[Main Documentation](docs/README.md)**: Comprehensive project overview
- **[Dermatologist Tools](docs/DERMATOLOGIST_TOOL_README.md)**: Expert review tools
- **[Generation Guide](docs/ENHANCED_GENERATION_README.md)**: Image generation process
- **[Web Interface](docs/SWIPE_TOOL_README.md)**: Web-based annotation tool
- **[Strategy](docs/image_generation_strategy.md)**: Generation strategy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source. Please check the license file for details.

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the dermatologist tools in the `tools/` folder

## 🔗 Related Projects

- **Shine Skincare App**: [shineskincollective.com](https://shineskincollective.com)
- **Main Repository**: [github.com/sentilabs01/shine-skincare-app](https://github.com/sentilabs01/shine-skincare-app)

---

**Developed by:** [@sentilabs01](https://github.com/sentilabs01)  
**Website:** [shineskincollective.com](https://shineskincollective.com)

This synthetic data generation and curation tool is designed to create diverse, expert-validated datasets for AI-powered skin condition analysis and research.