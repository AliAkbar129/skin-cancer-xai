from functools import lru_cache
import torch
from torchvision.models import resnet18,ResNet18_Weights
@lru_cache(maxsize=1)
def encoder():
    torch.set_num_threads(2);weights=ResNet18_Weights.IMAGENET1K_V1
    model=resnet18(weights=weights).eval();model.fc=torch.nn.Identity()
    for p in model.parameters():p.requires_grad_(False)
    return model,weights.transforms()
def image_features(image):
    model,transform=encoder()
    with torch.inference_mode():return model(transform(image.convert('RGB')).unsqueeze(0))[0].numpy()
