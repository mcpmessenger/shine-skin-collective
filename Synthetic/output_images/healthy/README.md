# Healthy Skin Images

This folder contains images that have been identified by dermatologists as representing healthy skin conditions.

## Folder Structure

### `clear_skin/`
- Images with excellent skin quality
- No visible skin concerns
- Minimal to no blemishes, spots, or texture issues

### `minimal_concerns/`
- Images with very minor skin concerns
- Overall healthy appearance with slight variations
- May have 1-2 small blemishes or minor texture

### `well_maintained/`
- Images showing well-cared-for skin
- May have some natural aging signs but well-maintained
- Good skin health despite minor age-related changes

## Usage

These images serve as:
- **Control group** for ML model training
- **Baseline reference** for healthy skin classification
- **Negative examples** for condition detection models
- **Quality benchmarks** for synthetic data generation

## Metadata Structure

Each healthy image includes:
- `classification_targets`: All conditions set to `false`
- `severity_targets`: All conditions set to `none`
- `dermatologist_notes`: Professional assessment and recommendations
- `skin_quality`: Overall skin health rating

## Adding New Healthy Images

When adding new healthy images:
1. Copy the image to the appropriate subfolder
2. Create a corresponding JSON metadata file
3. Update the `classification_targets` to reflect healthy status
4. Add dermatologist assessment notes if available
