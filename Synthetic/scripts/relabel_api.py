#!/usr/bin/env python3
"""
Backend API for the dermatologist relabeling tool
Handles the actual file operations and metadata updates
"""

from flask import Flask, request, jsonify
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class RelabelAPI:
    def __init__(self, base_dir="../output_images"):
        self.base_dir = Path(base_dir)
        self.source_directories = [
            "output_images",
            "Synthetic Face Dataset", 
            "public/products"
        ]
        self.conditions = [
            "acne", "fine_lines_wrinkles", "aging", "hyperpigmentation", 
            "textured_skin", "redness", "pore_size", "healthy"
        ]
        self.severities = {
            "acne": ["mild", "moderate", "severe"],
            "fine_lines_wrinkles": ["mild", "moderate", "severe"],
            "aging": ["early_signs", "moderate", "advanced"],
            "hyperpigmentation": ["mild", "moderate", "severe"],
            "textured_skin": ["slight", "moderate", "severe"],
            "redness": ["mild", "moderate", "severe"],
            "pore_size": ["mild", "moderate", "severe"],
            "healthy": ["clear_skin", "minimal_concerns", "well_maintained"]
        }
    
    def get_all_images(self):
        """Get all images in the dataset with their current categories"""
        images = []
        
        for condition in self.conditions:
            condition_dir = self.base_dir / condition
            if not condition_dir.exists():
                continue
                
            for severity in self.severities.get(condition, []):
                severity_dir = condition_dir / severity
                if not severity_dir.exists():
                    continue
                    
                png_files = list(severity_dir.glob("*.png"))
                for png_file in png_files:
                    json_file = png_file.with_suffix('.json')
                    
                    # Load metadata if available
                    metadata = {}
                    if json_file.exists():
                        try:
                            with open(json_file, 'r') as f:
                                metadata = json.load(f)
                        except:
                            pass
                    
                    images.append({
                        'id': len(images) + 1,
                        'filename': png_file.name,
                        'currentCategory': condition,
                        'currentSeverity': severity,
                        'path': str(png_file.relative_to(self.base_dir)),
                        'metadata': metadata
                    })
        
        return images
    
    def move_image(self, image_path, new_condition, new_severity):
        """Move an image and its metadata to a new category"""
        try:
            source_path = self.base_dir / image_path
            json_path = source_path.with_suffix('.json')
            
            if not source_path.exists():
                return {"success": False, "error": "Source file not found"}
            
            # Create destination directory
            dest_dir = self.base_dir / new_condition / new_severity
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate new filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_image_name = f"{new_condition}_{new_severity}_{timestamp}_{source_path.stem.split('_')[-1]}.png"
            new_json_name = f"{new_condition}_{new_severity}_{timestamp}_{source_path.stem.split('_')[-1]}.json"
            
            dest_image_path = dest_dir / new_image_name
            dest_json_path = dest_dir / new_json_name
            
            # Copy files
            shutil.copy2(source_path, dest_image_path)
            
            # Update metadata if JSON exists
            if json_path.exists():
                shutil.copy2(json_path, dest_json_path)
                self.update_metadata(dest_json_path, new_condition, new_severity)
            else:
                # Create new metadata file
                self.create_metadata(dest_json_path, new_condition, new_severity, source_path.name)
            
            return {
                "success": True,
                "newPath": str(dest_image_path.relative_to(self.base_dir)),
                "newImageName": new_image_name
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_metadata(self, json_path, new_condition, new_severity):
        """Update the metadata file with new category information"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Store original information
            if 'original_condition' not in data:
                data['original_condition'] = data.get('skin_condition', 'unknown')
                data['original_severity'] = data.get('severity', 'unknown')
            
            # Update basic information
            data['skin_condition'] = new_condition
            data['severity'] = new_severity
            data['image_filename'] = Path(json_path).with_suffix('.png').name
            data['relabeled_at'] = datetime.now().isoformat()
            
            # Update classification targets
            data['classification_targets'] = {
                "acne": new_condition == "acne",
                "fine_lines_wrinkles": new_condition == "fine_lines_wrinkles",
                "aging": new_condition == "aging",
                "hyperpigmentation": new_condition == "hyperpigmentation",
                "textured_skin": new_condition == "textured_skin",
                "redness": new_condition == "redness",
                "pore_size": new_condition == "pore_size"
            }
            
            # Update severity targets
            data['severity_targets'] = {}
            for condition in self.conditions[:-1]:  # Exclude 'healthy'
                if condition == new_condition:
                    data['severity_targets'][condition] = new_severity
                else:
                    data['severity_targets'][condition] = "none"
            
            # Update training annotations
            if new_condition == "healthy":
                data['training_annotations'] = {
                    "condition_detected": False,
                    "severity_level": "healthy",
                    "confidence_score": 0.95,
                    "affected_percentage": 0.0,
                    "feature_count": 0
                }
            else:
                # Keep original annotations but update severity
                if 'training_annotations' not in data:
                    data['training_annotations'] = {}
                data['training_annotations']['severity_level'] = new_severity
                data['training_annotations']['condition_detected'] = True
            
            # Add dermatologist notes
            data['dermatologist_notes'] = {
                "relabeled": True,
                "original_condition": data.get('original_condition', 'unknown'),
                "original_severity": data.get('original_severity', 'unknown'),
                "new_condition": new_condition,
                "new_severity": new_severity,
                "relabeled_at": data['relabeled_at']
            }
            
            # Save updated metadata
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            logging.error(f"Error updating metadata: {e}")
    
    def create_metadata(self, json_path, condition, severity, original_filename):
        """Create new metadata file for images without existing metadata"""
        metadata = {
            "image_filename": Path(json_path).with_suffix('.png').name,
            "skin_condition": condition,
            "severity": severity,
            "generation_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "image_counter": 0,
            "training_annotations": {
                "condition_detected": condition != "healthy",
                "severity_level": severity,
                "confidence_score": 0.8,
                "affected_percentage": 0.1 if condition != "healthy" else 0.0,
                "feature_count": 5 if condition != "healthy" else 0
            },
            "classification_targets": {
                "acne": condition == "acne",
                "fine_lines_wrinkles": condition == "fine_lines_wrinkles",
                "aging": condition == "aging",
                "hyperpigmentation": condition == "hyperpigmentation",
                "textured_skin": condition == "textured_skin",
                "redness": condition == "redness",
                "pore_size": condition == "pore_size"
            },
            "severity_targets": {
                "acne": severity if condition == "acne" else "none",
                "fine_lines_wrinkles": severity if condition == "fine_lines_wrinkles" else "none",
                "aging": severity if condition == "aging" else "none",
                "hyperpigmentation": severity if condition == "hyperpigmentation" else "none",
                "textured_skin": severity if condition == "textured_skin" else "none",
                "redness": severity if condition == "redness" else "none",
                "pore_size": severity if condition == "pore_size" else "none"
            },
            "demographics": {
                "age_group": "adult",
                "age_range": "26-40",
                "skin_tone": "medium skin tone",
                "gender": "female",
                "variation_index": 0
            },
            "generation_details": {
                "prompt_used": "Relabeled by dermatologist",
                "model_used": "manual_relabeling",
                "api_version": "dermatologist_tool_v1.0"
            },
            "quality_metrics": {
                "image_resolution": "1024x1024",
                "lighting_quality": "natural",
                "pose_quality": "front-facing",
                "occlusion_level": "none"
            },
            "dermatologist_notes": {
                "relabeled": True,
                "original_filename": original_filename,
                "new_condition": condition,
                "new_severity": severity,
                "relabeled_at": datetime.now().isoformat()
            }
        }
        
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=4)
    
    def count_images_in_directory(self, directory):
        """Count images in a specific directory"""
        count = 0
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return 0
            
        for condition in self.conditions:
            condition_dir = dir_path / condition
            if not condition_dir.exists():
                continue
                
            for severity in self.severities.get(condition, []):
                severity_dir = condition_dir / severity
                if not severity_dir.exists():
                    continue
                    
                png_files = list(severity_dir.glob("*.png"))
                count += len(png_files)
        
        return count
    
    def get_images_from_directory(self, directory):
        """Get all images from a specific directory"""
        images = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return images
            
        for condition in self.conditions:
            condition_dir = dir_path / condition
            if not condition_dir.exists():
                continue
                
            for severity in self.severities.get(condition, []):
                severity_dir = condition_dir / severity
                if not severity_dir.exists():
                    continue
                    
                png_files = list(severity_dir.glob("*.png"))
                for png_file in png_files:
                    json_file = png_file.with_suffix('.json')
                    
                    # Load metadata if available
                    metadata = {}
                    if json_file.exists():
                        try:
                            with open(json_file, 'r') as f:
                                metadata = json.load(f)
                        except:
                            pass
                    
                    images.append({
                        'id': len(images) + 1,
                        'filename': png_file.name,
                        'currentCategory': condition,
                        'currentSeverity': severity,
                        'path': str(png_file.relative_to(dir_path)),
                        'sourceDirectory': directory,
                        'metadata': metadata
                    })
        
        return images
    
    def mirror_image_to_directory(self, image_path, target_directory):
        """Mirror an image to another directory"""
        try:
            # Find the source image
            source_path = None
            for directory in self.source_directories:
                test_path = Path(directory) / image_path
                if test_path.exists():
                    source_path = test_path
                    break
            
            if not source_path:
                return {"success": False, "error": "Source image not found"}
            
            # Create target directory structure
            target_dir = Path(target_directory)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the image
            target_path = target_dir / source_path.name
            shutil.copy2(source_path, target_path)
            
            # Copy metadata if it exists
            source_json = source_path.with_suffix('.json')
            if source_json.exists():
                target_json = target_path.with_suffix('.json')
                shutil.copy2(source_json, target_json)
            
            return {
                "success": True,
                "targetPath": str(target_path.relative_to(target_dir)),
                "message": f"Image mirrored to {target_directory}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize the API
relabel_api = RelabelAPI()

@app.route('/api/images', methods=['GET'])
def get_images():
    """Get all images in the dataset"""
    try:
        images = relabel_api.get_all_images()
        return jsonify({"success": True, "images": images})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/relabel', methods=['POST'])
def relabel_image():
    """Relabel a single image"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        new_condition = data.get('newCategory')
        new_severity = data.get('newSeverity')
        
        if not all([image_path, new_condition, new_severity]):
            return jsonify({"success": False, "error": "Missing required parameters"}), 400
        
        result = relabel_api.move_image(image_path, new_condition, new_severity)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/relabel-batch', methods=['POST'])
def relabel_batch():
    """Relabel multiple images"""
    try:
        data = request.get_json()
        changes = data.get('changes', [])
        
        results = []
        for change in changes:
            result = relabel_api.move_image(
                change['imagePath'],
                change['newCategory'],
                change['newSeverity']
            )
            results.append({
                'imageId': change.get('imageId'),
                'filename': change.get('filename'),
                'result': result
            })
        
        return jsonify({"success": True, "results": results})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/directories', methods=['GET'])
def get_directories():
    """Get available directories and their image counts"""
    try:
        directories = {}
        for directory in relabel_api.source_directories:
            dir_path = Path(directory)
            if dir_path.exists():
                count = relabel_api.count_images_in_directory(directory)
                directories[directory] = count
            else:
                directories[directory] = 0
        
        return jsonify({"success": True, "directories": directories})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/directories/<directory>', methods=['GET'])
def get_directory_images(directory):
    """Get images from a specific directory"""
    try:
        if directory == "all":
            images = []
            for dir_name in relabel_api.source_directories:
                dir_images = relabel_api.get_images_from_directory(dir_name)
                images.extend(dir_images)
        else:
            images = relabel_api.get_images_from_directory(directory)
        
        return jsonify({"success": True, "images": images})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mirror', methods=['POST'])
def mirror_image():
    """Mirror an image to multiple directories"""
    try:
        data = request.get_json()
        image_path = data.get('imagePath')
        target_directories = data.get('targetDirectories', [])
        
        if not image_path or not target_directories:
            return jsonify({"success": False, "error": "Missing required parameters"}), 400
        
        results = []
        for target_dir in target_directories:
            result = relabel_api.mirror_image_to_directory(image_path, target_dir)
            results.append({
                'directory': target_dir,
                'result': result
            })
        
        return jsonify({"success": True, "results": results})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("🔬 Starting Dermatologist Relabeling API...")
    print("📁 Base directory:", relabel_api.base_dir.absolute())
    print("🌐 API will be available at: http://localhost:5000")
    print("📋 Endpoints:")
    print("  GET  /api/images - Get all images")
    print("  POST /api/relabel - Relabel single image")
    print("  POST /api/relabel-batch - Relabel multiple images")
    print("  GET  /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
