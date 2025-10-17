# 🔬 Dermatologist Swipe Tool

A professional web-based interface for dermatologists to review, validate, and curate synthetic skin condition images with efficient navigation and expert annotation workflows.

## ✨ Features

### **Professional Review Interface**
- **Single image display** for focused examination
- **Large, clear images** (500px height) for detailed analysis
- **Arrow navigation** to move between images
- **Progress tracking** showing current position
- **Expert validation** workflow for synthetic data

### **Efficient Categorization**
- **Click-to-categorize** - just click the appropriate category zone
- **Single healthy category** - "Mark as Healthy" button for quick access
- **Auto-advance** - automatically moves to next image after categorization
- **Visual feedback** - category zones highlight when selected
- **Quality control** - easy deletion of poor-quality images

### **Professional Workflow**
- **Delete functionality** - remove unwanted images
- **Keyboard shortcuts** for faster operation
- **Batch saving** - save all changes at once
- **Session management** - reset and start over
- **Metadata updates** - automatic JSON file updates
- **Expert annotation** - dermatologist validation tracking

## 🎯 **Categories Available**

### **Skin Conditions:**
- **Acne** (Mild, Moderate, Severe)
- **Fine Lines & Wrinkles** (Mild, Moderate, Severe)
- **Aging** (Early Signs, Moderate, Advanced)
- **Hyperpigmentation** (Mild, Moderate, Severe)
- **Textured Skin** (Slight, Moderate, Severe)
- **Redness** (Mild, Moderate, Severe)
- **Pore Size** (Mild, Moderate, Severe)

### **Healthy Skin:**
- **Single "Healthy" category** for clear, well-maintained skin

## ⌨️ **Keyboard Shortcuts**

- **Arrow Left/Right** - Navigate between images
- **H** - Mark current image as healthy
- **Delete/Backspace** - Delete current image
- **1, 2, 3** - Quick categorize acne (mild, moderate, severe)

## 🚀 **How to Use**

### **1. Start the Tool**
```bash
# Windows Batch
start_swipe_tool.bat

# Windows PowerShell
.\start_swipe_tool.ps1
```

### **2. Load Images**
- Click **"Load Images"** to scan the dataset
- Images will appear one at a time for review

### **3. Review and Categorize**
- **Examine** the current image carefully
- **Click** the appropriate category zone to categorize
- **Use arrows** or keyboard to navigate between images
- **Mark as Healthy** for clear, well-maintained skin
- **Delete** unwanted or poor-quality images

### **4. Save Changes**
- Click **"Save All Changes"** to apply all categorizations
- Changes are automatically saved to metadata files

## 🎨 **Interface Layout**

### **Top Section:**
- **Controls** - Load, Save, Reset buttons
- **Progress Bar** - Shows current position in dataset
- **Status Messages** - Confirmation and error messages

### **Main Section:**
- **Large Image Display** - Current image for examination
- **Image Info** - Filename and current category
- **Navigation** - Previous/Next arrow buttons
- **Action Buttons** - Delete and Mark as Healthy

### **Bottom Section:**
- **Category Grid** - 3x6 grid of all skin condition categories
- **Click-to-Categorize** - Simply click the appropriate category

## 🔧 **Technical Details**

### **File Structure:**
```
dermatologist_swipe_tool.html    # Main interface
start_swipe_tool.bat            # Windows batch launcher
start_swipe_tool.ps1            # PowerShell launcher
relabel_api.py                  # Backend API (shared)
```

### **API Endpoints:**
- `GET /api/images` - Load all images from dataset
- `POST /api/relabel-batch` - Save all changes at once

### **Image Loading:**
- **Real images** loaded from dataset paths
- **Error handling** with placeholder for missing files
- **Fallback system** with sample data if API unavailable

## 🎯 **Workflow Benefits**

### **For Dermatologists:**
- **Focused review** - one image at a time
- **Quick categorization** - click and move on
- **Efficient navigation** - arrows and keyboard shortcuts
- **Simplified healthy** - single healthy category
- **Quality control** - easy deletion of poor images

### **For Data Quality:**
- **Consistent categorization** - standardized process
- **Batch processing** - efficient for large datasets
- **Metadata updates** - automatic JSON file updates
- **Session management** - track progress and changes

## 📱 **Responsive Design**

- **Desktop optimized** - designed for professional use
- **Large touch targets** - easy clicking on category zones
- **Clear typography** - readable text and labels
- **Professional styling** - clean, medical-grade interface

## 🔄 **Session Management**

- **Load Images** - Start a new review session
- **Save Changes** - Apply all categorizations
- **Reset Session** - Clear all changes and start over
- **Progress Tracking** - See how many images reviewed

This tool provides a streamlined, efficient workflow for dermatologists to quickly and accurately categorize skin condition images! 🎉

---

## Developer Information

**Developed by:** [@sentilabs01](https://github.com/sentilabs01/shine-skincare-app)  
**Website:** [shineskincollective.com](https://shineskincollective.com)

This streamlined dermatologist review tool is part of the Shine Skincare App project, designed to create efficient workflows for AI-powered skin condition analysis.
