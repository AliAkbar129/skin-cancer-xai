import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

# In a real scenario, you'd load the HAM10000 dataset using torchvision.datasets.ImageFolder
# and apply imblearn.over_sampling.SMOTE to the flattened images before training.

def get_weighted_loss(class_counts):
    """
    Computes weighted cross-entropy loss to handle class imbalance.
    """
    total = sum(class_counts)
    weights = [total / c for c in class_counts]
    weights = torch.FloatTensor(weights)
    return nn.CrossEntropyLoss(weight=weights)

def train_model():
    print("Initializing Hybrid CNN-ViT Model...")
    from model import HybridSkinCancerModel
    model = HybridSkinCancerModel(num_classes=7)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # Mock class counts for HAM10000
    class_counts = [327, 514, 1099, 115, 1113, 6705, 142]
    criterion = get_weighted_loss(class_counts).to(device)
    
    # AdamW Optimizer with weight decay
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    
    # Cosine Annealing Learning Rate Scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
    
    print("Model ready for training.")
    print("NOTE: Download HAM10000 dataset, apply SMOTE, and load via DataLoader to proceed.")

if __name__ == "__main__":
    train_model()
