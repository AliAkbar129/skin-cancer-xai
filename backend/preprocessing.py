import cv2
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

def dull_razor(img):
    """
    DullRazor algorithm for hair removal in dermoscopic images.
    Expects a PIL Image or OpenCV numpy array (BGR).
    """
    if isinstance(img, Image.Image):
        img_np = np.array(img.convert('RGB'))
        # Convert RGB to BGR for OpenCV
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    else:
        img_np = img
        
    # 1. Grayscale conversion
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    
    # 2. Morphological Black-Hat transform to find dark hair structures
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (17, 17))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    
    # 3. Enhance hair contours
    _, thresh = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    
    # 4. Inpaint the original image using the hair mask
    inpainted = cv2.inpaint(img_np, thresh, 1, cv2.INPAINT_TELEA)
    
    # Return as PIL RGB Image
    return Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))

def get_inference_transforms():
    """
    Returns the torchvision transforms for inference as described in the paper.
    (Resize 224x224, Normalize with ImageNet stats)
    """
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                             std=[0.229, 0.224, 0.225])
    ])

def preprocess_image(image_bytes):
    """
    Takes image bytes, runs DullRazor and applies transforms.
    """
    import io
    img = Image.open(io.BytesIO(image_bytes))
    img_no_hair = dull_razor(img)
    transform = get_inference_transforms()
    img_tensor = transform(img_no_hair).unsqueeze(0) # Add batch dim
    return img_tensor, img_no_hair
