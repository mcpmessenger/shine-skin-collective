# Tools Directory

This directory contains all dermatologist review and annotation tools for the Shine Synthetic Face Dataset.

## 📁 Tools Overview

### **Web-Based Tools**
- **`dermatologist_swipe_tool_server.html`** - Main web interface for image review
- **`dermatologist_swipe_tool.html`** - Alternative web interface

### **Launcher Scripts**
- **`start_dermatologist_server.bat`** - Windows batch launcher
- **`start_dermatologist_server.py`** - Python launcher
- **`start_full_system.bat`** - Full system launcher
- **`start_full_system.py`** - Full system Python launcher
- **`start_swipe_tool.bat`** - Swipe tool launcher
- **`start_swipe_tool.ps1`** - PowerShell launcher

## 🚀 Quick Start

### **Option 1: Web Interface (Recommended)**
```bash
# Windows
start_swipe_tool.bat

# PowerShell
.\start_swipe_tool.ps1
```

### **Option 2: Direct HTML**
```bash
# Open in browser
start dermatologist_swipe_tool_server.html
```

## 🎯 Features

### **Web-Based Annotation Interface**
- **Large Image Display**: Clear, detailed view of each image
- **Click-to-Categorize**: Easy category and severity selection
- **Batch Processing**: Save multiple changes at once
- **Quality Control**: Delete poor-quality images
- **Keyboard Shortcuts**: Fast navigation and labeling
- **Dark/Light Mode**: Comfortable viewing options

### **Supported Categories**
- **Healthy** (clear_skin, minimal_concerns, well_maintained)
- **Acne** (mild, moderate, severe)
- **Aging** (early_signs, moderate, advanced)
- **Hyperpigmentation** (mild, moderate, severe)
- **Textured Skin** (slight, moderate, severe)
- **Redness** (mild, moderate, severe)
- **Pore Size** (mild, moderate, severe)
- **Fine Lines & Wrinkles** (mild, moderate, severe)

### **Workflow Features**
- **Image Gallery**: Thumbnail view of all images
- **Progress Tracking**: Visual progress bar
- **Change Tracking**: Count of changes made
- **Auto-Advance**: Move to next image after labeling
- **Metadata Updates**: Automatic JSON file updates

## ⌨️ Keyboard Shortcuts

### **Navigation**
- **Arrow Left/Right**: Previous/Next image
- **Enter**: Save current label
- **Delete**: Delete current image

### **Categories (Number Keys)**
- **1**: Healthy
- **2**: Acne
- **3**: Aging
- **4**: Hyperpigmentation
- **5**: Textured Skin
- **6**: Redness
- **7**: Pore Size
- **8**: Fine Lines & Wrinkles

### **Severity (Letter Keys)**
- **M**: Mild
- **M**: Moderate (Shift+M)
- **S**: Severe

## 🔧 Usage Instructions

### **1. Load Images**
- Click "Load Images" button
- Tool will scan the `output_images` directory
- Images will appear in the gallery

### **2. Review Images**
- Click on any thumbnail to view full size
- Use arrow keys or navigation buttons to move between images
- Each image shows current category and severity

### **3. Label Images**
- Click appropriate category button
- Select severity level
- Click "Save Label" or press Enter
- Image will be moved to correct directory

### **4. Quality Control**
- Delete poor-quality images using "Delete" button
- Review all images before finalizing
- Use "Save All Changes" for batch processing

## 📊 Current Dataset Status

- **Total Images**: 311 (210 original + 101 new)
- **Ready for Review**: All images loaded and ready
- **API Quota**: Hit daily limit (generation paused)
- **Next Steps**: Complete generation after quota reset

## 🛠️ Troubleshooting

### **Images Not Loading**
- Check that `output_images` directory exists
- Ensure images are in correct subdirectories
- Check browser console for errors

### **Changes Not Saving**
- Verify file permissions
- Check that JSON metadata files exist
- Ensure output directories are writable

### **Tool Not Starting**
- Try different launcher script
- Check Python installation
- Verify all dependencies are installed

## 📚 Related Documentation

- **[Main README](../README.md)** - Project overview
- **[Scripts README](../scripts/README.md)** - Generation scripts
- **[Dermatologist Tool Guide](../docs/DERMATOLOGIST_TOOL_README.md)** - Detailed tool usage
- **[Swipe Tool Guide](../docs/SWIPE_TOOL_README.md)** - Web interface guide
