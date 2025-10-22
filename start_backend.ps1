# PowerShell script to start the Shine Skin Collective Backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Shine Skin Collective Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to ml-training directory
Set-Location -Path "ml-training"

# Set environment variables
$env:MODEL_CHECKPOINT = "..\checkpoints\best_model.pth"
$env:PORT = "8000"

Write-Host "Loading model from: $env:MODEL_CHECKPOINT" -ForegroundColor Yellow
Write-Host "Starting server on port: $env:PORT" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please wait - this may take 30-60 seconds to load the model..." -ForegroundColor Green
Write-Host "Once you see 'Application startup complete', the server is ready!" -ForegroundColor Green
Write-Host ""

# Start the inference server
python inference_server.py

