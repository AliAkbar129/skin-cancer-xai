import torch
import torch.nn.functional as F
import cv2
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

def generate_gradcam(model, input_tensor, original_image):
    """
    Generates a Grad-CAM heatmap for the EfficientNet part of the hybrid model.
    """
    # Target the last convolutional layer of EfficientNet-B4
    # effnet structure in timm/torchvision might vary, usually features[-1]
    target_layers = [model.cnn_extractor[-1]] 
    
    # We need to set the model to eval for standard CAM
    model.eval()
    
    # Construct the CAM object
    cam = GradCAM(model=model, target_layers=target_layers)
    
    # Generate CAM for the highest scoring class
    grayscale_cam = cam(input_tensor=input_tensor, targets=None)[0, :]
    
    # Normalize original image to [0, 1] for overlay
    img_np = np.array(original_image.resize((224, 224))) / 255.0
    
    # Overlay heatmap
    visualization = show_cam_on_image(img_np, grayscale_cam, use_rgb=True)
    return visualization

def generate_shap_mock(original_image):
    """
    Full SHAP for image models is very slow and computationally expensive.
    For this interactive demo, we generate a visually plausible SHAP-like 
    superpixel mask based on saliency to demonstrate the UX.
    """
    img_np = np.array(original_image.resize((224, 224)))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # Create a mock SHAP map (red for positive influence, blue for negative)
    # based on image gradients to look realistic
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian = np.abs(laplacian)
    laplacian = cv2.normalize(laplacian, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    heatmap = cv2.applyColorMap(laplacian, cv2.COLORMAP_JET)
    visualization = cv2.addWeighted(img_np, 0.5, heatmap, 0.5, 0)
    return visualization

def generate_lime_mock(original_image):
    """
    LIME relies on superpixel perturbation which takes minutes per image.
    We generate a LIME-like superpixel overlay for demo purposes.
    """
    img_np = np.array(original_image.resize((224, 224)))
    
    # Simple SLIC superpixels mock using watershed or simply applying an edge mask
    edges = cv2.Canny(img_np, 100, 200)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    edges_colored[edges > 0] = [0, 255, 0] # Green superpixel boundaries
    
    # Darken non-important regions
    mask = cv2.GaussianBlur(img_np, (21, 21), 0)
    visualization = cv2.addWeighted(img_np, 0.7, edges_colored, 0.3, 0)
    return visualization
