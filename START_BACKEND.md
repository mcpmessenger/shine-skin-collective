# 🚀 How to Start the Backend Server

## Quick Start

### Option 1: Using Batch File (Windows)
```batch
.\start_backend.bat
```

### Option 2: Using PowerShell Script (Windows)
```powershell
.\start_backend.ps1
```

### Option 3: Manual Start
```bash
cd ml-training
python inference_server.py
```
The server will automatically find the model at `../checkpoints/best_model.pth`.

## What Happens When You Start the Backend?

1. **Model Loading** (20-40 seconds): The FastAPI server loads the trained EfficientNet-B0 model from the checkpoint
2. **Server Start**: Uvicorn starts on `http://localhost:8000`
3. **Ready**: You'll see "Application startup complete" when ready

## Verify the Server is Running

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok"}
```

## API Endpoints

### 1. Health Check
- **URL**: `GET /health`
- **Response**: `{"status": "ok"}`

### 2. Skin Analysis Inference
- **URL**: `POST /infer`
- **Content-Type**: `multipart/form-data`
- **Body**: Form field `image` with image file
- **Response**:
```json
{
  "concerns": [
    {
      "name": "Acne",
      "severity": "moderate",
      "percentage": 45,
      "description": ""
    }
  ],
  "region_concerns": {
    "left_cheek": [...],
    "right_cheek": [...],
    "forehead": [...],
    "t_zone": [...],
    "chin": [...]
  }
}
```

## Testing the Inference Endpoint

### Using PowerShell
```powershell
$image = Get-Item "path\to\image.jpg"
$response = Invoke-WebRequest -Uri "http://localhost:8000/infer" `
    -Method Post `
    -Form @{image = $image} `
    -ContentType "multipart/form-data"
$response.Content | ConvertFrom-Json
```

### Using curl
```bash
curl -X POST "http://localhost:8000/infer" \
  -F "image=@path/to/image.jpg"
```

### Using Python
```python
import requests

with open("path/to/image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/infer",
        files={"image": f}
    )
    
print(response.json())
```

## Configuration

The server uses these environment variables (all optional):

- `MODEL_CHECKPOINT`: Path to the model checkpoint (default: `../checkpoints/best_model.pth`)
- `PORT`: Port to run the server on (default: `8000`)

Example:
```bash
set MODEL_CHECKPOINT=../checkpoints/best_model.pth
set PORT=8000
cd ml-training
python inference_server.py
```

## Troubleshooting

### Server won't start
1. **Check Python dependencies are installed**:
   ```bash
   cd ml-training
   pip install -r requirements.txt
   ```

2. **Verify checkpoint exists**:
   ```bash
   dir ..\checkpoints\best_model.pth
   ```

3. **Check port availability**:
   ```bash
   netstat -ano | findstr :8000
   ```

### Model architecture mismatch
The server automatically detects the model architecture from the checkpoint. The current checkpoint uses **EfficientNet-B0**.

### Slow loading
- **First load**: 20-40 seconds (loading PyTorch model)
- **GPU**: If you have CUDA, the server will automatically use it for faster inference
- **CPU**: Works fine but slightly slower inference (~200-500ms per image)

## Connecting Frontend to Backend

Once the backend is running on `http://localhost:8000`, update your Next.js frontend API routes to point to this URL:

1. Update `app/api/analyze/route.ts`:
```typescript
const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
const response = await fetch(`${backendUrl}/infer`, {
  method: 'POST',
  body: formData
});
```

2. Add to `.env.local`:
```env
BACKEND_URL=http://localhost:8000
```

## Deployment

For production deployment, see the [API_INTEGRATION.md](API_INTEGRATION.md) file for AWS Elastic Beanstalk deployment instructions.

## Performance

- **Inference Time**: < 200ms per image (CPU), < 50ms (GPU)
- **Model Size**: ~20MB (EfficientNet-B0)
- **Memory**: ~500MB RAM
- **Concurrent Requests**: Supports multiple concurrent requests via FastAPI async

## Next Steps

1. ✅ Start the backend server
2. 🌐 Start the Next.js frontend (`npm run dev`)
3. 🧪 Test the complete flow by uploading an image
4. 🚀 Deploy to AWS Elastic Beanstalk for production

