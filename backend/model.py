import torch
import torch.nn as nn
from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights
import timm

class AttentionFusion(nn.Module):
    def __init__(self, cnn_dim, vit_dim, out_dim):
        super(AttentionFusion, self).__init__()
        self.cnn_proj = nn.Linear(cnn_dim, out_dim)
        self.vit_proj = nn.Linear(vit_dim, out_dim)
        
        # Trainable attention coefficient alpha
        self.alpha = nn.Parameter(torch.tensor(0.5))
        
    def forward(self, cnn_feat, vit_feat):
        cnn_proj = self.cnn_proj(cnn_feat)
        vit_proj = self.vit_proj(vit_feat)
        
        # alpha * cnn + (1 - alpha) * vit
        # Constrain alpha between 0 and 1
        alpha_sig = torch.sigmoid(self.alpha)
        fused = alpha_sig * cnn_proj + (1 - alpha_sig) * vit_proj
        return fused

class HybridSkinCancerModel(nn.Module):
    def __init__(self, num_classes=7, dropout_prob=0.4):
        super(HybridSkinCancerModel, self).__init__()
        
        # Local feature extractor: EfficientNet-B4
        effnet = efficientnet_b4(weights=EfficientNet_B4_Weights.IMAGENET1K_V1)
        self.cnn_extractor = nn.Sequential(*list(effnet.children())[:-1]) # Remove classifier
        # EfficientNet-B4 output channels is 1792
        self.cnn_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Global feature extractor: ViT-Base/16
        # Pretrained ViT on ImageNet
        self.vit = timm.create_model('vit_base_patch16_224', pretrained=True)
        self.vit.head = nn.Identity() # Remove the classifier head
        # ViT-B/16 output dim is 768
        
        # Attention Fusion Layer
        fused_dim = 1024
        self.fusion = AttentionFusion(cnn_dim=1792, vit_dim=768, out_dim=fused_dim)
        
        # Classification Head
        self.bn = nn.BatchNorm1d(fused_dim)
        self.dropout = nn.Dropout(p=dropout_prob) # Also used for MC-Dropout during inference
        self.fc = nn.Linear(fused_dim, num_classes)
        
    def forward(self, x):
        # Local features
        cnn_feat = self.cnn_extractor(x)
        cnn_feat = self.cnn_pool(cnn_feat).flatten(1)
        
        # Global features
        vit_feat = self.vit(x)
        
        # Attention-guided fusion
        fused = self.fusion(cnn_feat, vit_feat)
        
        # Regularization and Classification
        out = self.bn(fused)
        out = self.dropout(out)
        logits = self.fc(out)
        
        return logits

    def enable_mc_dropout(self):
        """Enable dropout during inference for uncertainty estimation."""
        for m in self.modules():
            if m.__class__.__name__.startswith('Dropout'):
                m.train()
