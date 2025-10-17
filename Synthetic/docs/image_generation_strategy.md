# Image Generation Strategy and Annotation System

## Image Generation Prompts

We will generate images for the following skin conditions:

*   **Acne:**
    *   Mild acne: "Close-up of a face with a few small, scattered pimples and blackheads, clear skin otherwise, natural lighting."
    *   Moderate acne: "Close-up of a face with several inflamed red pimples, some whiteheads, and blackheads, slightly oily skin, natural lighting."
    *   Severe acne: "Close-up of a face with numerous large, inflamed cysts and nodules, significant redness and scarring, oily skin, harsh lighting."

*   **Fine Lines & Wrinkles:**
    *   Mild fine lines: "Close-up of an eye area with subtle fine lines around the outer corners, smooth skin texture, soft lighting."
    *   Moderate wrinkles: "Close-up of a forehead with visible wrinkles, some deeper lines, and slightly uneven skin tone, natural lighting."
    *   Severe wrinkles: "Close-up of a face with deep wrinkles on the forehead, around the eyes, and mouth, sagging skin, uneven pigmentation, harsh lighting."

*   **Aging:**
    *   Early aging signs: "Close-up of a face with some loss of elasticity, a few fine lines, and slight dullness, natural lighting."
    *   Moderate aging: "Close-up of a face with noticeable wrinkles, some sagging, age spots, and uneven skin tone, natural lighting."
    *   Advanced aging: "Close-up of an elderly face with pronounced wrinkles, significant sagging, prominent age spots, and thin, fragile skin, harsh lighting."

*   **Hyperpigmentation:**
    *   Mild hyperpigmentation: "Close-up of a face with a few light brown spots (freckles or sun spots), otherwise clear skin, natural lighting."
    *   Moderate hyperpigmentation: "Close-up of a face with several darker brown patches (melasma or post-inflammatory hyperpigmentation), uneven skin tone, natural lighting."
    *   Severe hyperpigmentation: "Close-up of a face with widespread dark brown to black patches, significant discoloration, and uneven skin texture, harsh lighting."

*   **Textured Skin:**
    *   Slightly textured skin: "Close-up of a face with slightly uneven skin texture, some minor bumps or roughness, natural lighting."
    *   Moderately textured skin: "Close-up of a face with noticeable rough patches, small bumps, and enlarged pores, natural lighting."
    *   Severely textured skin: "Close-up of a face with significant unevenness, prominent bumps, scars, and large pores, harsh lighting."

*   **Redness & Pore Size:**
    *   Mild redness & pore size: "Close-up of a face with slight redness, particularly on the cheeks, and slightly visible pores, natural lighting."
    *   Moderate redness & pore size: "Close-up of a face with noticeable redness, some broken capillaries, and clearly visible enlarged pores, natural lighting."
    *   Severe redness & pore size: "Close-up of a face with widespread intense redness, prominent broken capillaries, and very large, open pores, harsh lighting."

## Annotation Structure

For each generated image, we will create a JSON annotation file with the following structure, inspired by the `test_image_analysis.py` script:

```json
{
    "image_filename": "image_name.png",
    "skin_condition": "acne",
    "severity": "mild",
    "annotations": {
        "detected": true,
        "percentage": 0.X, // Estimated percentage of affected area
        "spot_count": Y,   // Estimated number of spots/features
        "confidence": 0.Z  // Confidence score (can be a placeholder for synthetic data)
    },
    "prompt_used": "Full text prompt used for generation"
}
```

## Storage

Generated images will be stored in a directory structure like `output_images/condition_name/severity/image_name.png`. Corresponding JSON annotation files will be stored alongside the images, e.g., `output_images/condition_name/severity/image_name.json`.

