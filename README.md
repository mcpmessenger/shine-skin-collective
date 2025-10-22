# Shine Skin Collective

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/williamtflynn-2750s-projects/v0-shine-skincare-app)
[![Built with Next.js](https://img.shields.io/badge/Built%20with-Next.js-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![Machine Learning](https://img.shields.io/badge/ML-Enabled-blue?style=for-the-badge&logo=tensorflow)](https://tensorflow.org/)

## Overview

Shine Skin Collective is an advanced skincare analysis platform that combines cutting-edge machine learning with a modern web interface to provide personalized skin condition analysis and product recommendations. The platform uses a comprehensive synthetic dataset of 3000+ skin images to train multi-label classification models for accurate skin condition detection and severity assessment.

## 🚀 Key Features

- **Multi-label Skin Classification**: Detects 7 primary skin conditions (acne, aging, fine lines, hyperpigmentation, pore size, redness, textured skin)
- **Severity Assessment**: Predicts severity levels for each detected condition
- **Dual Input Methods**: Camera capture OR photo upload from gallery
- **Real-time Analysis**: Fast inference capabilities with <100ms processing time
- **Synthetic Dataset**: 3000+ high-quality synthetic images with comprehensive annotations
- **Modern UI/UX**: Built with Next.js, React, and Tailwind CSS
- **RESTful API**: Easy integration for external applications
- **Comprehensive Documentation**: Detailed guides for developers and ML engineers

## 📁 Project Structure

```
shine-skin-collective/
├── app/                    # Next.js application pages and API routes
├── components/             # React components and UI library
├── docs/                   # Comprehensive documentation
│   ├── Developer_Integration_Instructions.md
│   ├── ML_Model_Training_Plan.md
│   └── README.md
├── Synthetic/              # Synthetic dataset and ML tools
│   ├── output_images/      # 3000+ synthetic skin images
│   ├── scripts/            # Data generation and processing tools
│   └── docs/               # Dataset documentation
├── lib/                    # Utility functions and types
└── public/                 # Static assets
```

## 🛠️ Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Python 3.11 (for ML backend)

### Frontend Setup

1. Clone the repository:
```bash
git clone https://github.com/mcpmessenger/shine-skin-collective.git
cd shine-skin-collective
```

2. Install frontend dependencies:
```bash
npm install
# or
yarn install
```

3. Run the Next.js development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Using the App

**Camera Mode** (Default):
- Position your face in the circle
- Real-time face detection indicator
- Tap the camera button to capture and analyze

**Photo Upload Mode** (New!):
- Click the "Upload" button in the top-right
- Select a photo from your device gallery
- Preview the selected image
- Tap "Analyze" to process the photo

Both modes provide the same AI-powered skin analysis with 7 skin conditions and severity levels!

### Backend Setup (ML Inference Server)

1. Install Python dependencies:
```bash
cd ml-training
pip install -r requirements.txt
```

2. Start the FastAPI backend server:
```bash
# Option 1: Use the startup script (Windows)
.\start_backend.bat

# Option 2: Manual start
cd ml-training
python inference_server.py
```

3. The backend runs on [http://localhost:8000](http://localhost:8000)

4. Verify it's working:
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

📖 **Detailed Backend Instructions**: See [START_BACKEND.md](START_BACKEND.md) for complete documentation

## 📚 Documentation

### For Developers
- **[Developer Integration Instructions](docs/Developer_Integration_Instructions.md)** - Complete guide for integrating the ML model
- **[API Integration Guide](API_INTEGRATION.md)** - API endpoints and specifications
- **[Technical Requirements](Shine%20Skincare%20App%20v2%20Technical%20Product%20Requirements%20Document.md)** - Detailed product specifications

### For ML Engineers
- **[ML Model Training Plan](docs/ML_Model_Training_Plan.md)** - Comprehensive training strategy
- **[Synthetic Dataset Documentation](Synthetic/README.md)** - Dataset structure and usage
- **[Data Generation Guide](Synthetic/docs/DATA_GENERATION_PLAN.md)** - Synthetic data creation process

### For Data Scientists
- **[Dataset Statistics](Synthetic/docs/)** - Comprehensive data analysis
- **[Generation Strategy](Synthetic/docs/image_generation_strategy.md)** - Data generation methodology

## 🔧 Technical Stack

- **Frontend**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS, Radix UI components
- **ML Framework**: TensorFlow/PyTorch (configurable)
- **Data Processing**: Python, NumPy, OpenCV, Pillow
- **API**: RESTful endpoints with JSON responses
- **Deployment**: Vercel, Docker support

## 📊 Dataset Overview

The synthetic dataset includes:
- **3,000+ high-resolution images** across 7 skin conditions
- **Multiple severity levels** per condition
- **Comprehensive JSON annotations** with demographic data
- **Quality validation tools** for data integrity
- **Preprocessing pipelines** for model training

## 🎯 Performance Targets

- **Classification Accuracy**: F1-score > 0.85
- **Inference Speed**: < 100ms per image
- **API Response Time**: < 500ms end-to-end
- **Model Size**: Optimized for mobile deployment

## 🤝 Contributing

We welcome contributions! Please see our documentation for guidelines on:
- Model training and evaluation
- API integration and testing
- Data generation and validation
- Code contributions and pull requests

## 📞 Support

For questions or support:
- Review the documentation in the `docs/` directory
- Check the synthetic dataset tools in `Synthetic/tools/`
- Refer to the API integration guide for technical issues

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
