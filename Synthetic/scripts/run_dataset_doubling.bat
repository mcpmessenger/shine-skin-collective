@echo off
echo ========================================
echo  Dataset Doubling with Horizontal Flips
echo ========================================
echo.
echo This will create flipped versions of all images
echo to double the dataset size from 311 to 622+ images
echo.
echo Cost savings: ~$9.33 (vs. generating new images)
echo.
pause

echo.
echo Starting dataset doubling...
python double_dataset_with_flips.py

echo.
echo ========================================
echo  Dataset Doubling Complete!
echo ========================================
pause
