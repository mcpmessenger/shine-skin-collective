"""
FastAPI inference server for Shine Skin Collective
Runs the trained PyTorch model and returns concerns + scores.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import torch
from torchvision import transforms
from PIL import Image
import io
import os

from model_architecture import create_model
import mediapipe as mp


class InferenceResponse(BaseModel):
    concerns: list[dict]
    region_concerns: dict | None = None


def load_model(checkpoint_path: str, device: str = "cpu"):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model = create_model("resnet50", pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"], strict=False)
    model.eval()
    model.to(device)
    return model


device = "cuda" if torch.cuda.is_available() else "cpu"
CHECKPOINT = os.getenv("MODEL_CHECKPOINT", "ml-training/checkpoints/best_model.pth")
model = load_model(CHECKPOINT, device=device)

preprocess = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/infer", response_model=InferenceResponse)
async def infer(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    data = await image.read()
    pil = Image.open(io.BytesIO(data)).convert("RGB")
    tensor = preprocess(pil).unsqueeze(0).to(device)

    # Prepare face mesh to get regions
    mp_face_mesh = mp.solutions.face_mesh
    mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
    region_concerns = None

    # Run face mesh on original image for ROI masks
    img_np = np.array(pil)
    results = mesh.process(img_np)

    # Helper to run model on a PIL image crop
    def run_infer_on_pil(p: Image.Image):
        t = preprocess(p).unsqueeze(0).to(device)
        with torch.no_grad():
            return model(t)

    # Full-face inference
    outputs = run_infer_on_pil(pil)
    condition_probs = outputs["condition_logits"].cpu().numpy().tolist()[0]
    condition_names = [
        "acne",
        "aging",
        "fine_lines_wrinkles",
        "hyperpigmentation",
        "pore_size",
        "redness",
        "textured_skin",
    ]
    concerns = []
    for i, name in enumerate(condition_names):
        prob = float(condition_probs[i])
        if prob < 0.2:
            severity = "mild"
        elif prob < 0.4:
            severity = "moderate"
        else:
            severity = "severe"
        concerns.append({
            "name": name.replace("_", " ").title(),
            "severity": severity,
            "percentage": round(prob * 100),
            "description": "",  # filled on frontend/mock
        })

    # If landmarks found, compute simple polygon ROIs and run per-ROI inference
    try:
        import numpy as np
        if results.multi_face_landmarks:
            h, w = img_np.shape[:2]
            lm = results.multi_face_landmarks[0].landmark

            def pts(idxs):
                return [(int(lm[i].x * w), int(lm[i].y * h)) for i in idxs]

            # Basic ROI index groups (approx): cheeks, forehead, nose (T-zone), chin, eyes
            left_cheek_idx = [234, 93, 137, 177, 215, 227, 234]
            right_cheek_idx = [454, 323, 361, 401, 429, 447, 454]
            forehead_idx = [10, 338, 297, 332, 284, 251, 389, 356, 454, 234, 127, 162, 10]
            nose_tzone_idx = [168, 6, 197, 195, 5, 4, 45, 275, 4, 195, 197, 6, 168]
            chin_idx = [152, 377, 400, 379, 365, 397, 365, 379, 400, 377, 152]

            rois = {
                "left_cheek": pts(left_cheek_idx),
                "right_cheek": pts(right_cheek_idx),
                "forehead": pts(forehead_idx),
                "t_zone": pts(nose_tzone_idx),
                "chin": pts(chin_idx),
            }

            region_concerns = {}
            for name, poly in rois.items():
                mask = Image.new('L', (w, h), 0)
                import PIL.ImageDraw as ImageDraw
                ImageDraw.Draw(mask).polygon(poly, outline=1, fill=1)
                masked = Image.new('RGB', (w, h))
                masked.paste(pil, mask=mask)

                # Crop bbox around polygon to reduce empty space
                xs = [p[0] for p in poly]
                ys = [p[1] for p in poly]
                bbox = (max(min(xs), 0), max(min(ys), 0), min(max(xs), w), min(max(ys), h))
                crop = masked.crop(bbox)
                out_roi = run_infer_on_pil(crop)
                probs = out_roi["condition_logits"].cpu().numpy().tolist()[0]
                region_concerns[name] = [
                    {"name": cn.replace("_", " ").title(), "severity": ("mild" if p < 0.2 else "moderate" if p < 0.4 else "severe"), "percentage": round(p * 100)}
                    for cn, p in zip(condition_names, probs)
                ]
    except Exception:
        # If anything fails, just skip regions
        region_concerns = None

    return {"concerns": concerns, "region_concerns": region_concerns}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))


