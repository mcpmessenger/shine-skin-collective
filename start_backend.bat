@echo off
echo ========================================
echo Starting Shine Skin Collective Backend
echo ========================================
echo.

cd ml-training
set MODEL_CHECKPOINT=..\checkpoints\best_model.pth
set PORT=8000

echo Loading model from: %MODEL_CHECKPOINT%
echo Starting server on port: %PORT%
echo.
echo Please wait - this may take 30-60 seconds to load the model...
echo.

python inference_server.py

pause

