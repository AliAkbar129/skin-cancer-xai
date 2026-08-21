import io
import base64
import torch
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model import HybridSkinCancerModel
from preprocessing import preprocess_image
from xai import generate_gradcam, generate_shap_mock, generate_lime_mock

app = FastAPI(title="Skin Cancer XAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model (Using random weights for demo since we haven't trained on 3GB dataset)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = HybridSkinCancerModel(num_classes=7).to(device)
model.eval()

CLASSES = ['Actinic Keratoses (akiec)', 'Basal Cell Carcinoma (bcc)', 
           'Benign Keratosis (bkl)', 'Dermatofibroma (df)', 
           'Melanoma (mel)', 'Melanocytic Nevi (nv)', 'Vascular Lesions (vasc)']

def image_to_base64(img_np):
    img_pil = Image.fromarray(img_np)
    buffered = io.BytesIO()
    img_pil.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    # 1. Preprocess
    input_tensor, img_no_hair = preprocess_image(image_bytes)
    input_tensor = input_tensor.to(device)
    
    # 2. Standard Inference
    model.eval()
    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy()[0]
        
    # 3. Monte Carlo Dropout for Uncertainty
    model.enable_mc_dropout()
    mc_preds = []
    num_mc_samples = 15
    with torch.no_grad():
        for _ in range(num_mc_samples):
            mc_logits = model(input_tensor)
            mc_probs = torch.nn.functional.softmax(mc_logits, dim=1).cpu().numpy()[0]
            mc_preds.append(mc_probs)
            
    mc_preds = np.array(mc_preds)
    mean_probs = mc_preds.mean(axis=0)
    variance = mc_preds.var(axis=0).mean() # Mean variance across all classes
    
    # Calculate a simplified "Uncertainty Score" between 0 and 1
    uncertainty_score = min(variance * 100, 1.0) # Scaling for UI
    
    # 4. Generate XAI Maps
    gradcam_np = generate_gradcam(model, input_tensor, img_no_hair)
    shap_np = generate_shap_mock(img_no_hair)
    lime_np = generate_lime_mock(img_no_hair)
    
    # Find top prediction
    top_class_idx = np.argmax(mean_probs)
    top_class_name = CLASSES[top_class_idx]
    top_class_prob = float(mean_probs[top_class_idx])
    
    return {
        "prediction": top_class_name,
        "probability": top_class_prob,
        "uncertainty": float(uncertainty_score),
        "all_probabilities": {CLASSES[i]: float(mean_probs[i]) for i in range(7)},
        "xai": {
            "gradcam": image_to_base64(gradcam_np),
            "shap": image_to_base64(shap_np),
            "lime": image_to_base64(lime_np)
        }
    }
