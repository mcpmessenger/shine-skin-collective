import google.generativeai as genai
import os
import json
from PIL import Image
import io
import time
import requests
import base64
from datetime import datetime
import random

# Configure Gemini API: prefer GOOGLE_API_KEY (fallback to OPENAI_API_KEY for convenience)
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing API key. Set environment variable GOOGLE_API_KEY with your Google API key."
    )
genai.configure(api_key=api_key)

# Number of images to generate per condition/severity
IMAGES_PER_CONDITION = int(os.environ.get("IMAGES_PER_CONDITION", "10"))

# Demographic variations for diversity
DEMOGRAPHIC_VARIATIONS = [
    {"age_group": "young_adult", "age_range": "18-25", "description": "young adult"},
    {"age_group": "adult", "age_range": "26-40", "description": "adult"},
    {"age_group": "middle_aged", "age_range": "41-60", "description": "middle-aged"},
    {"age_group": "senior", "age_range": "60+", "description": "senior"},
    {"age_group": "elderly", "age_range": "70+", "description": "elderly"}
]

SKIN_TONE_VARIATIONS = [
    "very fair skin tone",
    "fair skin tone", 
    "light skin tone",
    "medium skin tone",
    "olive skin tone",
    "tan skin tone",
    "brown skin tone",
    "dark skin tone"
]

GENDER_VARIATIONS = ["male", "female", "non-binary"]

# Enhanced image generation data with diverse prompts
IMAGE_DATA = {
    "acne": {
        "mild": {
            "base_prompt": "Portrait showing a face with a few small, scattered pimples and blackheads, clear skin otherwise, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.05, "spot_count": 5, "confidence": 0.8}
        },
        "moderate": {
            "base_prompt": "Portrait showing a face with several inflamed red pimples, some whiteheads, and blackheads, slightly oily skin, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.15, "spot_count": 15, "confidence": 0.9}
        },
        "severe": {
            "base_prompt": "Front-facing portrait with many inflamed red pimples and a few small cysts, realistic human proportions, moderate redness and some light scarring, natural soft lighting, natural skin texture, not exaggerated or grotesque.",
            "annotations": {"detected": True, "percentage": 0.22, "spot_count": 22, "confidence": 0.93}
        }
    },
    "fine_lines_wrinkles": {
        "mild": {
            "base_prompt": "Portrait showing a face with subtle fine lines around the outer eye corners, smooth skin texture, soft lighting.",
            "annotations": {"detected": True, "percentage": 0.03, "spot_count": 3, "confidence": 0.75}
        },
        "moderate": {
            "base_prompt": "Portrait showing a face with visible wrinkles on forehead, some deeper lines, and slightly uneven skin tone, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.10, "spot_count": 10, "confidence": 0.85}
        },
        "severe": {
            "base_prompt": "Portrait showing a face with deep wrinkles on the forehead, around the eyes, and mouth, sagging skin, uneven pigmentation, harsh lighting.",
            "annotations": {"detected": True, "percentage": 0.25, "spot_count": 25, "confidence": 0.92}
        }
    },
    "aging": {
        "early_signs": {
            "base_prompt": "Portrait showing a face with some loss of elasticity, a few fine lines, and slight dullness, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.07, "spot_count": 7, "confidence": 0.8}
        },
        "moderate": {
            "base_prompt": "Portrait showing a face with noticeable wrinkles, some sagging, age spots, and uneven skin tone, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.18, "spot_count": 18, "confidence": 0.88}
        },
        "advanced": {
            "base_prompt": "Portrait showing an elderly face with pronounced wrinkles, significant sagging, prominent age spots, and thin, fragile skin, harsh lighting.",
            "annotations": {"detected": True, "percentage": 0.35, "spot_count": 35, "confidence": 0.95}
        }
    },
    "hyperpigmentation": {
        "mild": {
            "base_prompt": "Portrait showing a face with a few light brown spots (freckles or sun spots), otherwise clear skin, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.04, "spot_count": 4, "confidence": 0.78}
        },
        "moderate": {
            "base_prompt": "Portrait showing a face with several darker brown patches (melasma or post-inflammatory hyperpigmentation), uneven skin tone, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.12, "spot_count": 12, "confidence": 0.87}
        },
        "severe": {
            "base_prompt": "Front-facing portrait with pronounced, well-defined hyperpigmented patches (melasma and post-inflammatory hyperpigmentation) on cheeks and forehead; distinct, irregular edges with realistic variation in tone (medium to dark brown), visible pores and natural skin texture showing through; avoid muddy smears; soft even lighting for clinical clarity.",
            "annotations": {"detected": True, "percentage": 0.22, "spot_count": 18, "confidence": 0.92}
        }
    },
    "textured_skin": {
        "slight": {
            "base_prompt": "Portrait showing a face with slightly uneven skin texture, some minor bumps or roughness, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.06, "spot_count": 6, "confidence": 0.77}
        },
        "moderate": {
            "base_prompt": "Portrait showing a face with noticeable rough patches, small bumps, and enlarged pores, natural lighting.",
            "annotations": {"detected": True, "percentage": 0.16, "spot_count": 16, "confidence": 0.86}
        },
        "severe": {
            "base_prompt": "Portrait showing a face with significant unevenness, prominent bumps, scars, and large pores, harsh lighting.",
            "annotations": {"detected": True, "percentage": 0.32, "spot_count": 32, "confidence": 0.94}
        }
    },
    "redness": {
        "mild": {
            "base_prompt": "Front-facing portrait with subtle facial erythema focused on cheeks and around nose, light diffused redness with visible natural skin texture, soft even lighting.",
            "annotations": {"detected": True, "percentage": 0.08, "spot_count": 0, "confidence": 0.80}
        },
        "moderate": {
            "base_prompt": "Front-facing portrait with noticeable facial redness across cheeks and nose, a few visible superficial capillaries, realistic color variation, soft even lighting.",
            "annotations": {"detected": True, "percentage": 0.16, "spot_count": 0, "confidence": 0.88}
        },
        "severe": {
            "base_prompt": "Front-facing portrait with widespread facial erythema on cheeks, nose, and chin, distinct but realistic telangiectasia in areas, natural skin detail preserved, soft even lighting, not oversaturated.",
            "annotations": {"detected": True, "percentage": 0.30, "spot_count": 0, "confidence": 0.93}
        }
    },
    "pore_size": {
        "mild": {
            "base_prompt": "Front-facing portrait with slightly visible pores around the nose and central cheeks; realistic skin texture with gentle shine, soft lighting.",
            "annotations": {"detected": True, "percentage": 0.05, "spot_count": 0, "confidence": 0.78}
        },
        "moderate": {
            "base_prompt": "Front-facing portrait with clearly visible enlarged pores on nose and cheeks; realistic texture, mild oiliness, even lighting for clinical clarity.",
            "annotations": {"detected": True, "percentage": 0.12, "spot_count": 0, "confidence": 0.86}
        },
        "severe": {
            "base_prompt": "Front-facing portrait with large, open pores prominently visible on the T-zone and cheeks; detailed yet natural texture, no blur, soft even lighting.",
            "annotations": {"detected": True, "percentage": 0.22, "spot_count": 0, "confidence": 0.92}
        }
    }
}

# Output directory (override with environment variable OUTPUT_DIR); defaults to ./output_images
OUTPUT_DIR = os.environ.get("OUTPUT_DIR") or os.path.join(os.getcwd(), "output_images")

# Model can be overridden with GEMINI_IMAGE_MODEL
MODEL_ID = os.environ.get(
    "GEMINI_IMAGE_MODEL", "models/gemini-2.0-flash-preview-image-generation"
)

# Delay between requests to avoid rate limits (seconds)
DELAY_SECONDS = int(os.environ.get("GENERATION_DELAY_SECONDS", "30"))

# Prefix added to every prompt to encourage full-face selfie composition optimized for face detection
SELFIE_PREFIX = os.environ.get(
    "SELFIE_PREFIX",
    (
        "Generate a realistic photographic selfie of a single person, "
        "front-facing portrait with full face clearly visible from chin to forehead, "
        "shoulders and upper chest included in frame, centered composition, "
        "eye-level camera angle, neutral background, even soft lighting, "
        "eyes open and looking at camera, no occlusions, no hands or objects "
        "blocking the face, proper distance from camera (not too close, not too far), "
        "high resolution, sharp focus on facial features, suitable for face detection algorithms. "
        "Apply the following specific skin details:"
    ),
)

def generate_diverse_prompt(base_prompt, variation_index):
    """Generate a diverse prompt by adding demographic and variation details"""
    demographic = DEMOGRAPHIC_VARIATIONS[variation_index % len(DEMOGRAPHIC_VARIATIONS)]
    skin_tone = SKIN_TONE_VARIATIONS[variation_index % len(SKIN_TONE_VARIATIONS)]
    gender = GENDER_VARIATIONS[variation_index % len(GENDER_VARIATIONS)]
    
    # Add variation to the base prompt
    diverse_prompt = f"{base_prompt} The person should be a {demographic['description']} {gender} with {skin_tone}."
    
    return diverse_prompt, {
        "age_group": demographic["age_group"],
        "age_range": demographic["age_range"],
        "skin_tone": skin_tone,
        "gender": gender,
        "variation_index": variation_index
    }

def create_training_metadata(condition, severity, annotations, demographics, image_filename, prompt_used, generation_timestamp, image_counter):
    """Create comprehensive metadata for training purposes"""
    return {
        # Basic identification
        "image_filename": image_filename,
        "skin_condition": condition,
        "severity": severity,
        "generation_timestamp": generation_timestamp,
        "image_counter": image_counter,
        
        # Training annotations
        "training_annotations": {
            "condition_detected": annotations["detected"],
            "severity_level": severity,
            "confidence_score": annotations["confidence"],
            "affected_percentage": annotations["percentage"],
            "feature_count": annotations.get("spot_count", 0)
        },
        
        # Multi-label classification targets (for training)
        "classification_targets": {
            "acne": condition == "acne" and annotations["detected"],
            "fine_lines_wrinkles": condition == "fine_lines_wrinkles" and annotations["detected"],
            "aging": condition == "aging" and annotations["detected"],
            "hyperpigmentation": condition == "hyperpigmentation" and annotations["detected"],
            "textured_skin": condition == "textured_skin" and annotations["detected"],
            "redness": condition == "redness" and annotations["detected"],
            "pore_size": condition == "pore_size" and annotations["detected"]
        },
        
        # Severity targets (for training)
        "severity_targets": {
            "acne": severity if condition == "acne" and annotations["detected"] else "none",
            "fine_lines_wrinkles": severity if condition == "fine_lines_wrinkles" and annotations["detected"] else "none",
            "aging": severity if condition == "aging" and annotations["detected"] else "none",
            "hyperpigmentation": severity if condition == "hyperpigmentation" and annotations["detected"] else "none",
            "textured_skin": severity if condition == "textured_skin" and annotations["detected"] else "none",
            "redness": severity if condition == "redness" and annotations["detected"] else "none",
            "pore_size": severity if condition == "pore_size" and annotations["detected"] else "none"
        },
        
        # Demographic information
        "demographics": demographics,
        
        # Generation details
        "generation_details": {
            "prompt_used": prompt_used,
            "model_used": MODEL_ID,
            "api_version": "gemini-2.0-flash-preview"
        },
        
        # Quality metrics (for future validation)
        "quality_metrics": {
            "image_resolution": "1024x1024",  # Gemini default
            "lighting_quality": "natural",
            "pose_quality": "front-facing",
            "occlusion_level": "none"
        }
    }

def generate_and_annotate_images():
    """Generate diverse synthetic skin images with comprehensive metadata"""
    # Use REST API for image generation to explicitly request image output
    normalized_model = MODEL_ID
    if normalized_model.startswith("models/"):
        normalized_model = normalized_model.split("/", 1)[1]
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{normalized_model}:generateContent"
    )
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    # Request both text and image modalities as required by the image-generation model
    generation_config = {"responseModalities": ["TEXT", "IMAGE"]}

    # Counter for unique filenames across all generations
    global_image_counter = 0
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create main output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create dataset summary
    dataset_summary = {
        "generation_timestamp": start_time,
        "total_conditions": len(IMAGE_DATA),
        "images_per_condition": IMAGES_PER_CONDITION,
        "total_expected_images": len(IMAGE_DATA) * 3 * IMAGES_PER_CONDITION,  # 7 conditions * 3 severities * 10 images
        "generated_images": 0,
        "conditions": list(IMAGE_DATA.keys())
    }

    print(f"Starting generation of {dataset_summary['total_expected_images']} images...")
    print(f"Generating {IMAGES_PER_CONDITION} images per condition/severity combination")

    for condition, severities in IMAGE_DATA.items():
        for severity, data in severities.items():
            output_subdir = os.path.join(OUTPUT_DIR, condition, severity)
            os.makedirs(output_subdir, exist_ok=True)

            print(f"\nGenerating {IMAGES_PER_CONDITION} images for {condition} - {severity}...")
            
            for i in range(IMAGES_PER_CONDITION):
                # Generate diverse prompt
                diverse_prompt, demographics = generate_diverse_prompt(data["base_prompt"], i)
                full_prompt = f"{SELFIE_PREFIX} {diverse_prompt}"
                
                try:
                    payload = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": full_prompt}],
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
                        print(f"Error generating image {i+1}/{IMAGES_PER_CONDITION} for {condition} - {severity}: {resp.status_code} {err}")
                        continue
                    else:
                        data_json = resp.json()
                        candidates = data_json.get("candidates", [])
                        if not candidates:
                            print(f"No candidates found for image {i+1}/{IMAGES_PER_CONDITION} for {condition} - {severity}")
                            continue
                            
                        for candidate in candidates:
                            content = candidate.get("content", {})
                            parts = content.get("parts", [])
                            if not parts:
                                print(f"No content parts found for image {i+1}/{IMAGES_PER_CONDITION} for {condition} - {severity}")
                                continue
                                
                            for part in parts:
                                inline = part.get("inlineData") or part.get("inline_data")
                                if inline and inline.get("data"):
                                    image_bytes = io.BytesIO(base64.b64decode(inline["data"]))
                                    image = Image.open(image_bytes)

                                    # Generate unique filename
                                    image_filename = f"{condition}_{severity}_{start_time}_{global_image_counter:04d}.png"
                                    image_path = os.path.join(output_subdir, image_filename)
                                    image.save(image_path)
                                    print(f"Saved image {i+1}/{IMAGES_PER_CONDITION}: {image_filename}")

                                    # Create comprehensive annotation file
                                    annotation_filename = f"{condition}_{severity}_{start_time}_{global_image_counter:04d}.json"
                                    annotation_path = os.path.join(output_subdir, annotation_filename)

                                    annotation_data = create_training_metadata(
                                        condition, severity, data["annotations"], demographics,
                                        image_filename, full_prompt, start_time, global_image_counter
                                    )
                                    
                                    with open(annotation_path, "w") as f:
                                        json.dump(annotation_data, f, indent=4)
                                    print(f"Saved annotation: {annotation_filename}")
                                    
                                    # Update counters
                                    global_image_counter += 1
                                    dataset_summary["generated_images"] += 1
                                    break
                                else:
                                    print(f"No inline image data returned for image {i+1}/{IMAGES_PER_CONDITION} for {condition} - {severity}")
                except Exception as e:
                    print(f"Error generating image {i+1}/{IMAGES_PER_CONDITION} for {condition} - {severity}: {e}")

                # Respect delay between API calls to mitigate rate limits
                if DELAY_SECONDS > 0 and i < IMAGES_PER_CONDITION - 1:  # Don't delay after last image
                    print(f"Waiting {DELAY_SECONDS}s before next generation...")
                    time.sleep(DELAY_SECONDS)

    # Save dataset summary
    summary_path = os.path.join(OUTPUT_DIR, f"dataset_summary_{start_time}.json")
    with open(summary_path, "w") as f:
        json.dump(dataset_summary, f, indent=4)
    
    print(f"\nGeneration complete!")
    print(f"Generated {dataset_summary['generated_images']} images out of {dataset_summary['total_expected_images']} expected")
    print(f"Dataset summary saved to: {summary_path}")

if __name__ == "__main__":
    generate_and_annotate_images()
