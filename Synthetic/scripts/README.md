# Scripts Directory

This directory contains all Python scripts for the Shine Synthetic Face Dataset project.

## 📁 Scripts Overview

### **Core Generation Scripts**
- **`generate_skin_images_enhanced.py`** - Main image generation script using Gemini API
- **`relabel_api.py`** - CLI tool for relabeling and moving images
- **`changes_server.py`** - Server for tracking changes made during review
- **`save_changes_api.py`** - API for saving changes to the dataset

## 🚀 Usage

### **Generate Images**
```bash
# Set API key
set GOOGLE_API_KEY=your_api_key_here

# Generate full dataset (210 images)
python generate_skin_images_enhanced.py

# Generate with custom settings
set IMAGES_PER_CONDITION=5
set GENERATION_DELAY_SECONDS=15
python generate_skin_images_enhanced.py
```

### **Relabel Images**
```bash
# Start CLI relabeling tool
python relabel_api.py

# Start as server
python relabel_api.py --server
```

### **Track Changes**
```bash
# Start change tracking server
python changes_server.py

# Save changes
python save_changes_api.py
```

## ⚙️ Configuration

### **Environment Variables**
- `GOOGLE_API_KEY` - Required for image generation
- `IMAGES_PER_CONDITION` - Images per condition/severity (default: 10)
- `OUTPUT_DIR` - Output directory (default: ./output_images)
- `GENERATION_DELAY_SECONDS` - Delay between API calls (default: 30)

### **API Quota Management**
- **Free Tier**: 100 requests per day
- **Current Status**: Hit quota limit (101 images generated)
- **Reset Time**: 24 hours from last request
- **Remaining**: 109 images to complete doubling

## 📊 Current Status

- **Images Generated**: 311 total (210 original + 101 new)
- **API Quota**: Hit daily limit
- **Next Run**: Wait 24 hours for quota reset
- **Remaining Images**: 109 to complete the doubling

## 🔧 Troubleshooting

### **API Key Issues**
```bash
# Check if API key is set
echo %GOOGLE_API_KEY%

# Set API key
set GOOGLE_API_KEY=your_key_here
```

### **Quota Exceeded**
- Wait 24 hours for quota reset
- Check Google AI Studio for quota status
- Consider upgrading to paid plan for higher limits

### **File Path Issues**
- Use forward slashes in paths
- Ensure output directory exists
- Check file permissions

## 📚 Related Documentation

- **[Main README](../README.md)** - Project overview
- **[Dermatologist Tools](../docs/DERMATOLOGIST_TOOL_README.md)** - Expert review tools
- **[Generation Guide](../docs/ENHANCED_GENERATION_README.md)** - Detailed generation process
