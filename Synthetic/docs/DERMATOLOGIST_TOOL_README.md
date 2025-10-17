# Dermatologist Re-labeling Tool

Professional utility for dermatologists to review, re-categorize, and curate synthetic skin condition images with automatic metadata updates.

## 🎯 Problem Solved

- **Manual Process**: No need to manually move files and edit JSON metadata
- **Automatic Updates**: Metadata is automatically updated when images are moved
- **Batch Operations**: Can move multiple images at once
- **Error Prevention**: Validates paths and categories before moving
- **Expert Validation**: Enables dermatologists to validate AI-generated synthetic data
- **Quality Control**: Streamlined workflow for dataset curation

## 🚀 Quick Start

### Option 1: Command line
```bash
python relabel_api.py
```

### Option 2: Web Interface (Recommended)
```bash
# Start the web-based annotation tool
start_swipe_tool.bat          # Windows
# or
.\start_swipe_tool.ps1        # PowerShell
```

### Option 3: Direct API
```bash
# Start the Flask API server
python relabel_api.py --server
```

## 📋 How to Use

### **Command Line Interface**
1. **List All Images**: See all images in the dataset with their current categories
2. **Move Single Image**: Enter path, select new condition and severity
3. **Batch Move Images**: Process multiple images from a directory

### **Web Interface (Recommended)**
1. **Load Images**: Click "Load Images" to scan the dataset
2. **Review One-by-One**: Large, clear images for detailed examination
3. **Click-to-Categorize**: Click appropriate category zone to categorize
4. **Batch Save**: Save all changes at once
5. **Quality Control**: Delete poor-quality images

### **API Endpoints**
- `GET /api/images` - Load all images from dataset
- `POST /api/relabel-batch` - Save all changes at once
- `POST /api/relabel-single` - Relabel individual image

## 📁 Supported Categories

### **Skin Conditions**
- `acne` (mild, moderate, severe)
- `fine_lines_wrinkles` (mild, moderate, severe)
- `aging` (early_signs, moderate, advanced)
- `hyperpigmentation` (mild, moderate, severe)
- `textured_skin` (slight, moderate, severe)
- `redness` (mild, moderate, severe)
- `pore_size` (mild, moderate, severe)
- `healthy` (clear_skin, minimal_concerns, well_maintained)

## 🔄 What Happens When You Move an Image

1. **File Movement**: Both `.png` and `.json` files are moved to new location
2. **Metadata Update**: JSON file is automatically updated with:
   - New condition and severity
   - Updated classification targets
   - Updated severity targets
   - Relabeling timestamp
   - Original condition tracking
3. **New Filenames**: Files get new names with timestamp for uniqueness

## 📝 Example Workflow

```
1. Run: python dermatologist_relabel_tool.py
2. Select: "2. Move/relabel an image"
3. Enter path: output_images/acne/mild/acne_mild_20250910_163628_0001.png
4. Select condition: 1 (acne)
5. Select severity: 2 (severe)
6. Result: Image moved to acne/severe/ with updated metadata
```

## ⚠️ Important Notes

- **Backup First**: Always backup your data before bulk operations
- **File Paths**: Use full paths or relative paths from the tool directory
- **Metadata Integrity**: The tool preserves all original metadata while updating categories
- **No Data Loss**: Original files are copied, not moved (unless you choose to delete originals)

## 🛠️ Troubleshooting

### "Source file not found"
- Check the file path is correct
- Make sure the file exists
- Use forward slashes or double backslashes in paths

### "Metadata file not found"
- Ensure there's a corresponding `.json` file
- The JSON file should have the same name as the PNG file

### "Invalid condition selection"
- Use the numbers provided in the menu
- Make sure you're selecting a valid option

## 📞 Support

For issues or questions about the relabeling tool, please check the main project documentation or contact the development team.
