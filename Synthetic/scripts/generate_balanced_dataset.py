#!/usr/bin/env python3
"""
Generate Balanced Dataset
Focuses on generating images for underrepresented conditions to balance the dataset

Priority Order:
1. Redness: +134 images
2. Pore Size: +134 images
3. Textured Skin: +130 images
4. Hyperpigmentation: +122 images

Total: 520 images, ~$15.60, ~5 hours
Expected improvement: 85% → 90-95% accuracy
"""

import os
import json
from PIL import Image
import io
import time
from datetime import datetime
import random
import logging
import requests
import base64

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini API
API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing API key. Set GOOGLE_API_KEY environment variable.")

# Configuration
IMAGES_PER_SEVERITY = 45  # Target per severity level
GENERATION_DELAY = int(os.environ.get("GENERATION_DELAY_SECONDS", "30"))
OUTPUT_DIR = "output_images"

# Demographics for diversity
SKIN_TONES = [
    "very fair skin tone (Fitzpatrick I)",
    "fair skin tone (Fitzpatrick II)",
    "medium skin tone (Fitzpatrick III)",
    "olive skin tone (Fitzpatrick IV)",
    "tan brown skin tone (Fitzpatrick V)",
    "deep brown skin tone (Fitzpatrick VI)"
]

AGE_GROUPS = [
    {"range": "18-25", "desc": "young adult"},
    {"range": "26-35", "desc": "adult"},
    {"range": "36-50", "desc": "middle-aged"},
    {"range": "51-65", "desc": "mature"}
]

GENDERS = ["female", "male", "person"]

# ENHANCED PROMPTS - Highly specific to distinguish conditions
BALANCED_IMAGE_DATA = {
    "redness": {
        "mild": {
            "count_needed": 45,
            "base_prompt": """Face with VERY SUBTLE FACIAL REDNESS appearing as a gentle pink flush 
concentrated on the cheeks and nose, with maybe 1-2 tiny visible broken capillaries. 
The redness should be mild and barely noticeable, giving a slightly flushed appearance. 
The rest of the face should have clear, even-toned skin with NO raised acne bumps, 
NO brown dark spots, NO texture issues - ONLY subtle pink coloration."""
        },
        "moderate": {
            "count_needed": 45,
            "base_prompt": """Face with CLEAR FACIAL REDNESS appearing as noticeable pink-red coloration 
on the cheeks, nose, and chin, with several visible broken capillaries (small red spider veins). 
The redness should be obvious but not extreme, similar to rosacea. Skin should otherwise be 
smooth with NO raised acne bumps, NO brown dark spots, NO rough texture - ONLY redness 
and broken capillaries."""
        },
        "severe": {
            "count_needed": 44,
            "base_prompt": """Face with INTENSE WIDESPREAD FACIAL REDNESS covering most of the cheeks, 
nose, forehead, and chin with a deep red or purple hue. Include numerous visible broken 
capillaries and blood vessels creating a web-like pattern. The skin should appear inflamed 
and flushed but with NO raised pimples or pustules (pure redness, not acne), NO brown spots 
(not hyperpigmentation), and smooth surface texture. Severe rosacea appearance."""
        }
    },
    "pore_size": {
        "mild": {
            "count_needed": 45,
            "base_prompt": """Face with SLIGHTLY ENLARGED PORES visible primarily on the nose and 
inner cheeks when viewed closely. The pores appear as tiny dots or pinpoint openings, creating 
a subtle texture. Pores should be just barely visible, requiring close inspection. Skin is 
otherwise smooth and clear with NO acne bumps, NO redness, NO dark spots - ONLY slight pore 
visibility on nose area."""
        },
        "moderate": {
            "count_needed": 45,
            "base_prompt": """Face with CLEARLY VISIBLE ENLARGED PORES on the nose, cheeks, and forehead. 
The pores appear as distinct small dark dots giving a textured appearance to the skin, similar to 
subtle orange-peel texture. Each pore is clearly visible as a small opening. Skin may appear 
slightly oily. NO active acne bumps, NO widespread redness, NO brown dark spots - ONLY enlarged 
pore openings creating dots across the skin."""
        },
        "severe": {
            "count_needed": 44,
            "base_prompt": """Face with VERY LARGE, PROMINENT PORES visible across the entire face 
creating a pronounced orange-peel texture. The pores are very obvious, appearing as large dark 
openings on the nose, cheeks, chin, and forehead - like large dots covering the skin. Each pore 
is clearly visible and creates heavy texture. Skin appears very textured from pore visibility. 
NO raised acne, NO redness patches, NO dark spot discoloration - ONLY very enlarged pores."""
        }
    },
    "textured_skin": {
        "slight": {
            "count_needed": 44,
            "base_prompt": """Face with SLIGHTLY ROUGH OR BUMPY SKIN TEXTURE with minor surface 
irregularities visible when light hits the face at an angle. Include a few very small raised 
bumps or minimal roughness on the cheeks or forehead creating subtle shadows. The surface 
should appear slightly uneven. Skin tone is even (NO dark spots), NO active acne inflammation, 
NO redness - ONLY subtle texture/roughness/tiny bumps."""
        },
        "moderate": {
            "count_needed": 43,
            "base_prompt": """Face with NOTICEABLE BUMPY, ROUGH SKIN TEXTURE with visible surface 
irregularities creating shadows and uneven light reflection. Include some shallow acne scars 
(rolling scars), bumps, or rough patches on cheeks creating clear texture. The SURFACE is visibly 
uneven with bumps and depressions. Skin tone is relatively even (minimal dark spots), NO active 
red acne, just TEXTURE and surface irregularities."""
        },
        "severe": {
            "count_needed": 43,
            "base_prompt": """Face with SIGNIFICANTLY ROUGH, BUMPY SKIN with pronounced texture 
irregularities including visible ACNE SCARRING (ice-pick scars, rolling scars, boxcar scars), 
raised bumps, and rough patches creating heavy shadowing. The skin surface is clearly uneven, 
bumpy, and textured with deep pitted scars and raised areas. Skin tone is relatively even, 
NO active inflamed acne, NO widespread redness - ONLY severe texture/scarring/bumps."""
        }
    },
    "hyperpigmentation": {
        "mild": {
            "count_needed": 41,
            "base_prompt": """Face with 5-10 SMALL DARK BROWN SPOTS or areas of darker pigmentation 
scattered on the cheeks or forehead. These are FLAT (not raised), appearing as slightly darker 
patches or freckle-like marks against otherwise even-toned skin. The spots should be brown/tan, 
clearly darker than surrounding skin. NO raised bumps (not acne), NO overall pink/red flush, 
NO rough texture - ONLY brown pigmentation spots."""
        },
        "moderate": {
            "count_needed": 41,
            "base_prompt": """Face with MULTIPLE DARK BROWN SPOTS AND PATCHES across cheeks, forehead, 
and temples, creating noticeably uneven skin tone. Include larger patches of darker pigmentation 
(melasma-like) mixed with smaller brown spots. All pigmentation is FLAT (same smooth texture as 
rest of skin), brown/tan in color, clearly visible. NO raised areas, NO red inflammation, 
NO bumpy texture - ONLY brown color variation/patches."""
        },
        "severe": {
            "count_needed": 40,
            "base_prompt": """Face with EXTENSIVE DARK BROWN TO BLACK PATCHES covering large areas 
of the cheeks, forehead, upper lip, and temples. The hyperpigmentation creates a very uneven, 
splotchy appearance with significant contrast between darker brown/black and lighter areas. 
Large melasma-like patches dominate the face. All areas are FLAT and smooth (no texture difference), 
NO raised bumps, NO red coloration - ONLY dark brown/black pigmentation creating patchwork appearance."""
        }
    }
}

# Base prompt template for all images
BASE_PROMPT_TEMPLATE = """Photorealistic selfie, single {gender}, {age_desc} ({age_range} years old), 
with {skin_tone}, front-facing, eyes to camera, full head and shoulders fully visible with small 
margin around hairline and chin, subject centered, portrait orientation, face occupies ~40-60% of frame, 
even soft lighting, plain light-gray background, no hats, masks, sunglasses, hands, or hair covering 
the face. 

CONDITION SPECIFIC: {condition_prompt}

IMPORTANT: The face should show ONLY the specified condition. Skin should be otherwise clear and 
healthy-looking except for the described condition. Do not mix multiple skin issues."""


def generate_image_with_gemini(prompt, output_filename):
    """Generate a single image using Gemini REST API"""
    try:
        logger.info(f"Generating: {os.path.basename(output_filename)}")
        
        # Use Gemini 2.0 Flash Exp with direct REST API
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        generation_config = {
            "responseModalities": ["TEXT", "IMAGE"]  # KEY: Request image generation!
        }
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": generation_config,
        }
        
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        
        if resp.status_code != 200:
            try:
                err = resp.json()
            except Exception:
                err = {"message": resp.text}
            logger.error(f"❌ API Error {resp.status_code}: {err}")
            return False
        
        data_json = resp.json()
        candidates = data_json.get("candidates", [])
        
        if not candidates:
            logger.warning("⚠️ No candidates in response")
            return False
        
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            
            for part in parts:
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    # Decode and save image
                    image_bytes = io.BytesIO(base64.b64decode(inline["data"]))
                    image = Image.open(image_bytes)
                    image.save(output_filename, 'PNG')
                    logger.info(f"✅ Saved successfully")
                    return True
        
        logger.warning("⚠️ No image data in response")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False


def generate_balanced_dataset():
    """Generate images for underrepresented conditions"""
    logger.info("=" * 80)
    logger.info("BALANCED DATASET GENERATION")
    logger.info("=" * 80)
    logger.info(f"Target: 520 new images")
    logger.info(f"Cost estimate: ~$15.60")
    logger.info(f"Time estimate: ~5 hours (with delays)")
    logger.info("=" * 80)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    total_generated = 0
    total_failed = 0
    
    # Generate for each condition
    for condition, severities in BALANCED_IMAGE_DATA.items():
        logger.info(f"\n{'='*80}")
        logger.info(f"GENERATING: {condition.upper()}")
        logger.info(f"{'='*80}")
        
        for severity, config in severities.items():
            count_needed = config['count_needed']
            logger.info(f"\nSeverity: {severity} - Need {count_needed} images")
            
            # Create output directory
            output_dir = os.path.join(OUTPUT_DIR, condition, severity)
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate images
            for i in range(count_needed):
                # Random demographics
                skin_tone = random.choice(SKIN_TONES)
                age_group = random.choice(AGE_GROUPS)
                gender = random.choice(GENDERS)
                
                # Build full prompt
                full_prompt = BASE_PROMPT_TEMPLATE.format(
                    gender=gender,
                    age_desc=age_group['desc'],
                    age_range=age_group['range'],
                    skin_tone=skin_tone,
                    condition_prompt=config['base_prompt']
                )
                
                # Generate filename
                filename = f"{condition}_{severity}_{timestamp}_{total_generated:04d}.png"
                output_path = os.path.join(output_dir, filename)
                
                # Generate image
                success = generate_image_with_gemini(full_prompt, output_path)
                
                if success:
                    # Create metadata
                    metadata = {
                        "image_filename": filename,
                        "skin_condition": condition,
                        "severity": severity,
                        "generation_timestamp": timestamp,
                        "demographics": {
                            "age_range": age_group['range'],
                            "age_group": age_group['desc'],
                            "skin_tone": skin_tone,
                            "gender": gender
                        },
                        "classification_targets": {
                            cond: (cond == condition) for cond in BALANCED_IMAGE_DATA.keys()
                        },
                        "severity_targets": {
                            cond: severity if cond == condition else 'none' 
                            for cond in BALANCED_IMAGE_DATA.keys()
                        },
                        "training_annotations": {
                            "condition_detected": True,
                            "severity_level": severity,
                            "confidence_score": 0.9,
                            "is_balanced_generation": True
                        },
                        "prompt_used": full_prompt
                    }
                    
                    # Save metadata
                    json_path = output_path.replace('.png', '.json')
                    with open(json_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    total_generated += 1
                    logger.info(f"Progress: {total_generated}/520 ({total_generated/520*100:.1f}%)")
                else:
                    total_failed += 1
                
                # Delay between API calls
                if i < count_needed - 1:  # Don't delay after last image
                    logger.info(f"Waiting {GENERATION_DELAY}s before next image...")
                    time.sleep(GENERATION_DELAY)
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("GENERATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"✅ Images generated: {total_generated}")
    logger.info(f"❌ Failed: {total_failed}")
    logger.info(f"💰 Estimated cost: ${total_generated * 0.03:.2f}")
    logger.info("=" * 80)
    
    # Create summary file
    summary = {
        "generation_timestamp": timestamp,
        "images_generated": total_generated,
        "images_failed": total_failed,
        "conditions_generated": list(BALANCED_IMAGE_DATA.keys()),
        "purpose": "balance_dataset",
        "target_total_dataset_size": 1174,  # 654 existing + 520 new
        "estimated_cost": total_generated * 0.03
    }
    
    summary_path = os.path.join(OUTPUT_DIR, f"balanced_generation_summary_{timestamp}.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"\n📊 Summary saved to: {summary_path}")
    logger.info("\n🎉 Dataset balancing complete!")
    logger.info("Next step: Run double_dataset_with_flips.py to flip new images")
    logger.info("Then: Retrain model with python train_simple_conditions.py")


if __name__ == "__main__":
    logger.info("\n" + "🚨" * 40)
    logger.info("STARTING BALANCED DATASET GENERATION")
    logger.info("🚨" * 40)
    logger.info("\nThis will generate 520 new images for:")
    logger.info("  • Redness: 134 images")
    logger.info("  • Pore Size: 134 images")
    logger.info("  • Textured Skin: 130 images")
    logger.info("  • Hyperpigmentation: 122 images")
    logger.info(f"\n💰 Estimated cost: ~$15.60")
    logger.info(f"⏱️  Estimated time: ~5 hours (with {GENERATION_DELAY}s delays)")
    logger.info("\nPress Ctrl+C to cancel or wait 10 seconds to start...")
    
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        logger.info("\n❌ Generation canceled by user")
        exit(0)
    
    # Start generation
    generate_balanced_dataset()

