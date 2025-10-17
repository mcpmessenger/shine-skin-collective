#!/usr/bin/env python3
"""
Dermatologist Changes API
Handles saving changes made in the dermatologist swipe tool including:
- Moving images between categories/severities
- Updating metadata files
- Deleting images
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DermatologistChangesAPI:
    def __init__(self, dataset_root):
        self.dataset_root = Path(dataset_root)
        self.output_images_dir = self.dataset_root / "output_images"
        
        # Ensure output_images directory exists
        self.output_images_dir.mkdir(exist_ok=True)
        
        # Create backup directory for changes
        self.backup_dir = self.dataset_root / "changes_backup"
        self.backup_dir.mkdir(exist_ok=True)
    
    def move_image(self, filename, old_category, old_severity, new_category, new_severity, rename_file=True):
        """Move an image and its metadata from one category/severity to another"""
        try:
            # Define paths
            old_dir = self.output_images_dir / old_category / old_severity
            new_dir = self.output_images_dir / new_category / new_severity
            
            # Ensure new directory exists
            new_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate new filename if renaming is requested
            if rename_file:
                new_filename = self._generate_new_filename(filename, new_category, new_severity)
            else:
                new_filename = filename
            
            # File paths
            old_image_path = old_dir / filename
            new_image_path = new_dir / new_filename
            old_metadata_path = old_dir / filename.replace('.png', '.json')
            new_metadata_path = new_dir / new_filename.replace('.png', '.json')
            
            # Check if source files exist
            if not old_image_path.exists():
                raise FileNotFoundError(f"Image file not found: {old_image_path}")
            
            # Create backup before moving
            self._create_backup(old_image_path, old_metadata_path)
            
            # Move image file
            shutil.move(str(old_image_path), str(new_image_path))
            logger.info(f"Moved image: {old_image_path} -> {new_image_path}")
            
            # Move and update metadata file
            if old_metadata_path.exists():
                self._move_and_update_metadata(
                    old_metadata_path, 
                    new_metadata_path, 
                    new_category, 
                    new_severity,
                    new_filename
                )
            else:
                # Create new metadata file if it doesn't exist
                self._create_metadata_file(new_metadata_path, new_filename, new_category, new_severity)
            
            # Clean up empty old directory
            self._cleanup_empty_directory(old_dir)
            
            return {
                "success": True,
                "message": f"Successfully moved {filename} from {old_category}/{old_severity} to {new_category}/{new_severity}",
                "old_filename": filename,
                "new_filename": new_filename,
                "new_path": str(new_image_path.relative_to(self.dataset_root))
            }
            
        except Exception as e:
            logger.error(f"Error moving image {filename}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_image(self, filename, category, severity):
        """Delete an image and its metadata"""
        try:
            # Define paths
            image_dir = self.output_images_dir / category / severity
            image_path = image_dir / filename
            metadata_path = image_dir / filename.replace('.png', '.json')
            
            # Check if files exist
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Create backup before deleting
            self._create_backup(image_path, metadata_path)
            
            # Delete files
            image_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()
            
            logger.info(f"Deleted image: {image_path}")
            
            # Clean up empty directory
            self._cleanup_empty_directory(image_dir)
            
            return {
                "success": True,
                "message": f"Successfully deleted {filename} from {category}/{severity}"
            }
            
        except Exception as e:
            logger.error(f"Error deleting image {filename}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_process_changes(self, changes):
        """Process multiple changes in batch"""
        results = []
        successful_changes = 0
        filename_updates = {}  # Track filename changes for frontend updates
        
        for change in changes:
            if change.get('action') == 'move':
                # Check if we should rename files (default: True)
                rename_file = change.get('rename_file', True)
                
                result = self.move_image(
                    change['filename'],
                    change['oldCategory'],
                    change['oldSeverity'],
                    change['newCategory'],
                    change['newSeverity'],
                    rename_file
                )
                
                # Track filename changes for frontend updates
                if result.get('success') and 'new_filename' in result:
                    filename_updates[change['filename']] = result['new_filename']
                    
            elif change.get('action') == 'delete':
                result = self.delete_image(
                    change['filename'],
                    change['category'],
                    change['severity']
                )
            else:
                result = {
                    "success": False,
                    "error": f"Unknown action: {change.get('action')}"
                }
            
            results.append({
                "change": change,
                "result": result
            })
            
            if result.get('success'):
                successful_changes += 1
        
        return {
            "success": True,
            "message": f"Processed {len(changes)} changes, {successful_changes} successful",
            "results": results,
            "successful_count": successful_changes,
            "total_count": len(changes),
            "filename_updates": filename_updates
        }
    
    def _create_backup(self, image_path, metadata_path):
        """Create backup of files before making changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / timestamp
        backup_subdir.mkdir(exist_ok=True)
        
        if image_path.exists():
            shutil.copy2(str(image_path), str(backup_subdir / image_path.name))
        
        if metadata_path.exists():
            shutil.copy2(str(metadata_path), str(backup_subdir / metadata_path.name))
    
    def _generate_new_filename(self, old_filename, new_category, new_severity):
        """Generate a new filename based on the new category and severity"""
        # Extract the base name and extension
        name_parts = old_filename.split('.')
        if len(name_parts) < 2:
            return old_filename
        
        base_name = '.'.join(name_parts[:-1])
        extension = name_parts[-1]
        
        # Generate timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create new filename with pattern: {category}_{severity}_{timestamp}_{random}.{ext}
        import random
        random_suffix = f"{random.randint(1000, 9999):04d}"
        new_filename = f"{new_category}_{new_severity}_{timestamp}_{random_suffix}.{extension}"
        
        return new_filename
    
    def _move_and_update_metadata(self, old_metadata_path, new_metadata_path, new_category, new_severity, new_filename):
        """Move metadata file and update its content"""
        # Load existing metadata
        with open(old_metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Update metadata
        metadata['image_filename'] = new_filename
        metadata['skin_condition'] = new_category
        metadata['severity'] = new_severity
        metadata['last_modified'] = datetime.now().isoformat()
        
        # Update training annotations
        if 'training_annotations' in metadata:
            metadata['training_annotations']['condition_detected'] = True
            metadata['training_annotations']['severity_level'] = new_severity
        
        # Update classification targets
        if 'classification_targets' in metadata:
            for condition in metadata['classification_targets']:
                metadata['classification_targets'][condition] = (condition == new_category)
        
        # Update severity targets
        if 'severity_targets' in metadata:
            for condition in metadata['severity_targets']:
                metadata['severity_targets'][condition] = new_severity if condition == new_category else 'none'
        
        # Move and save updated metadata
        shutil.move(str(old_metadata_path), str(new_metadata_path))
        
        with open(new_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Updated metadata: {new_metadata_path}")
    
    def _create_metadata_file(self, metadata_path, filename, category, severity):
        """Create a new metadata file for an image"""
        metadata = {
            "image_filename": filename,
            "skin_condition": category,
            "severity": severity,
            "generation_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "last_modified": datetime.now().isoformat(),
            "training_annotations": {
                "condition_detected": True,
                "severity_level": severity,
                "confidence_score": 0.8,
                "affected_percentage": 0.1,
                "feature_count": 3
            },
            "classification_targets": {
                "acne": category == "acne",
                "fine_lines_wrinkles": category == "fine_lines_wrinkles",
                "aging": category == "aging",
                "hyperpigmentation": category == "hyperpigmentation",
                "textured_skin": category == "textured_skin",
                "redness": category == "redness",
                "pore_size": category == "pore_size",
                "healthy": category == "healthy"
            },
            "severity_targets": {
                "acne": severity if category == "acne" else "none",
                "fine_lines_wrinkles": severity if category == "fine_lines_wrinkles" else "none",
                "aging": severity if category == "aging" else "none",
                "hyperpigmentation": severity if category == "hyperpigmentation" else "none",
                "textured_skin": severity if category == "textured_skin" else "none",
                "redness": severity if category == "redness" else "none",
                "pore_size": severity if category == "pore_size" else "none",
                "healthy": severity if category == "healthy" else "none"
            }
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Created metadata file: {metadata_path}")
    
    def _cleanup_empty_directory(self, directory):
        """Remove empty directory if it has no files"""
        try:
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
                logger.info(f"Removed empty directory: {directory}")
        except OSError:
            pass  # Directory not empty or other error

# Example usage and testing
if __name__ == "__main__":
    # Test the API
    api = DermatologistChangesAPI(".")
    
    # Example: Move an image
    result = api.move_image(
        "acne_mild_0.png",
        "acne",
        "mild", 
        "acne",
        "moderate"
    )
    print("Move result:", result)
    
    # Example: Batch process changes
    changes = [
        {
            "action": "move",
            "filename": "test_image.png",
            "oldCategory": "acne",
            "oldSeverity": "mild",
            "newCategory": "acne", 
            "newSeverity": "moderate"
        }
    ]
    
    batch_result = api.batch_process_changes(changes)
    print("Batch result:", batch_result)
