#!/usr/bin/env python3
"""
Double Dataset Size by Creating Horizontally Flipped Versions
Creates mirror images of all synthetic skin images to double the dataset size

This is a cost-effective way to increase dataset size for training without
generating new images via API calls.
"""

import os
import json
import shutil
from pathlib import Path
from PIL import Image
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetDoubler:
    """Doubles dataset size by creating horizontally flipped versions of all images"""
    
    def __init__(self, dataset_root):
        self.dataset_root = Path(dataset_root)
        self.output_images_dir = self.dataset_root / "output_images"
        self.flipped_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
    def flip_image(self, image_path, output_path):
        """Flip an image horizontally and save it"""
        try:
            img = Image.open(image_path)
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            flipped_img.save(output_path)
            return True
        except Exception as e:
            logger.error(f"Error flipping image {image_path}: {str(e)}")
            return False
    
    def create_flipped_metadata(self, original_metadata, new_filename):
        """Create metadata for the flipped image"""
        flipped_metadata = original_metadata.copy()
        
        # Update filename
        flipped_metadata['image_filename'] = new_filename
        
        # Add flag indicating this is a flipped version
        flipped_metadata['is_flipped'] = True
        flipped_metadata['original_filename'] = original_metadata.get('image_filename', '')
        flipped_metadata['flip_timestamp'] = datetime.now().isoformat()
        
        # Keep all other metadata the same (condition, severity, etc.)
        return flipped_metadata
    
    def generate_flipped_filename(self, original_filename):
        """Generate a filename for the flipped version"""
        name_parts = original_filename.replace('.png', '').split('_')
        
        # Add 'flipped' indicator before the file extension
        flipped_filename = original_filename.replace('.png', '_flipped.png')
        
        return flipped_filename
    
    def process_directory(self, directory_path):
        """Process all images in a directory and create flipped versions"""
        logger.info(f"Processing directory: {directory_path.relative_to(self.dataset_root)}")
        
        # Get all PNG files
        png_files = list(directory_path.glob("*.png"))
        
        for png_file in png_files:
            # Skip if already a flipped version
            if '_flipped.png' in png_file.name:
                logger.debug(f"Skipping already flipped image: {png_file.name}")
                self.skipped_count += 1
                continue
            
            # Generate flipped filename
            flipped_filename = self.generate_flipped_filename(png_file.name)
            flipped_image_path = directory_path / flipped_filename
            
            # Skip if flipped version already exists
            if flipped_image_path.exists():
                logger.debug(f"Flipped version already exists: {flipped_filename}")
                self.skipped_count += 1
                continue
            
            # Flip the image
            if self.flip_image(png_file, flipped_image_path):
                logger.info(f"✓ Created flipped image: {flipped_filename}")
                
                # Handle metadata if it exists
                json_file = png_file.with_suffix('.json')
                if json_file.exists():
                    try:
                        # Load original metadata
                        with open(json_file, 'r') as f:
                            original_metadata = json.load(f)
                        
                        # Create flipped metadata
                        flipped_metadata = self.create_flipped_metadata(
                            original_metadata,
                            flipped_filename
                        )
                        
                        # Save flipped metadata
                        flipped_json_path = flipped_image_path.with_suffix('.json')
                        with open(flipped_json_path, 'w') as f:
                            json.dump(flipped_metadata, f, indent=2)
                        
                        logger.info(f"✓ Created flipped metadata: {flipped_json_path.name}")
                        
                    except Exception as e:
                        logger.error(f"Error creating flipped metadata for {json_file.name}: {str(e)}")
                        self.error_count += 1
                
                self.flipped_count += 1
            else:
                self.error_count += 1
    
    def process_all_conditions(self):
        """Process all conditions and severity levels"""
        logger.info("=" * 80)
        logger.info("DOUBLING DATASET WITH HORIZONTAL FLIPS")
        logger.info("=" * 80)
        
        conditions = [
            'acne', 'aging', 'fine_lines_wrinkles', 'hyperpigmentation',
            'pore_size', 'redness', 'textured_skin', 'healthy'
        ]
        
        total_dirs_processed = 0
        
        for condition in conditions:
            condition_dir = self.output_images_dir / condition
            
            if not condition_dir.exists():
                logger.warning(f"Condition directory not found: {condition_dir}")
                continue
            
            # Process all severity subdirectories
            for severity_dir in condition_dir.iterdir():
                if not severity_dir.is_dir():
                    continue
                
                self.process_directory(severity_dir)
                total_dirs_processed += 1
        
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Directories processed: {total_dirs_processed}")
        logger.info(f"Images flipped: {self.flipped_count}")
        logger.info(f"Images skipped (already flipped): {self.skipped_count}")
        logger.info(f"Errors: {self.error_count}")
        logger.info(f"\n✅ Dataset size approximately doubled!")
        logger.info(f"Original: ~311 images → New: ~{311 + self.flipped_count} images")
        logger.info("=" * 80)
    
    def create_summary_report(self):
        """Create a summary report of the doubling process"""
        summary = {
            "process": "horizontal_flip_augmentation",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "images_flipped": self.flipped_count,
                "images_skipped": self.skipped_count,
                "errors": self.error_count,
                "estimated_total_dataset_size": 311 + self.flipped_count
            },
            "benefits": {
                "cost_savings": f"${self.flipped_count * 0.03:.2f} (vs. generating new images)",
                "dataset_increase": f"{(self.flipped_count / 311) * 100:.1f}%"
            }
        }
        
        summary_path = self.output_images_dir / f"flip_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\n📊 Summary report saved to: {summary_path}")
        return summary


def main():
    """Main execution function"""
    # Get the dataset root
    script_dir = Path(__file__).parent
    dataset_root = script_dir.parent
    
    logger.info(f"Dataset root: {dataset_root}")
    
    # Create doubler instance
    doubler = DatasetDoubler(dataset_root)
    
    # Process all conditions
    doubler.process_all_conditions()
    
    # Create summary report
    summary = doubler.create_summary_report()
    
    logger.info("\n🎉 Dataset doubling complete!")
    logger.info(f"💰 Cost savings: {summary['benefits']['cost_savings']}")
    logger.info(f"📈 Dataset increase: {summary['benefits']['dataset_increase']}")


if __name__ == "__main__":
    main()
