<div align="center">
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/React-Dark.svg" width="60" height="60" alt="React" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/PyTorch-Dark.svg" width="60" height="60" alt="PyTorch" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg" width="60" height="60" alt="Python" />
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/TailwindCSS-Dark.svg" width="60" height="60" alt="Tailwind" />
  
  <br />
  <br />

  <h1 align="center">DermoAI XAI</h1>
  
  <p align="center">
    <strong>Attention-Guided Hybrid CNN–Vision Transformer Framework for Explainable Skin Cancer Classification</strong>
  </p>

  <p align="center">
    <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" /></a>
    <a href="https://reactjs.org/"><img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" /></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" /></a>
    <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" /></a>
  </p>

  <p align="center">
    <i>A full-stack, state-of-the-art clinical dashboard that solves the AI "Black Box" problem in Dermatology.</i>
  </p>
</div>

<hr />

## 🌟 Overview

This project is a high-performance web application implementing the architecture proposed in the research paper **"Attention-Guided Hybrid CNN–Vision Transformer Framework for Explainable Skin Cancer Classification"**. 

It is designed not just to accurately predict skin cancer (like Melanoma, Basal Cell Carcinoma, etc.), but to **explain its reasoning** to medical professionals using cutting-edge Explainable AI (XAI) and Uncertainty Quantification techniques.

### ✨ Key Features

- 🧠 **Hybrid Architecture**: Combines **EfficientNet-B4** (for local textures) and **ViT-Base/16** (for global structures) using a custom Attention-Guided Fusion mechanism.
- 🔍 **Explainable AI (XAI)**: Generates real-time **Grad-CAM**, **SHAP**, and **LIME** overlays directly in the browser to highlight diagnostically relevant lesion areas.
- 📊 **Uncertainty Quantification**: Utilizes **Monte Carlo Dropout** to calculate the variance of predictions, giving the model the ability to say *"I am uncertain, please consult a dermatologist."*
- 🎨 **Clinical Dashboard**: A stunning, animated, "Glassmorphism" React frontend featuring live metrics, scan history (via Local Storage), and real-time inference displays.
- ✂️ **Automated Preprocessing**: Implements the **DullRazor** algorithm (via OpenCV) to automatically identify and digitally remove hair from dermoscopic images before analysis.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/skin-cancer-xai.git
cd skin-cancer-xai
```

### 2. Backend Setup (Python API)
The backend requires Python 3.10+ and serves the PyTorch model via FastAPI.

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --reload
```
> **Note**: On the first launch, the server will take 1-3 minutes to download the massive pre-trained ViT and EfficientNet weights from HuggingFace.

### 3. Frontend Setup (React Dashboard)
Open a new terminal and start the Vite development server.

```bash
cd frontend
npm install
npm run dev -- --host
```

Open your browser to `http://localhost:5173`. Because we are using `--host`, you can also access this dashboard on your mobile phone if it's on the same Wi-Fi network!

---

## 🔬 Model Architecture

<div align="center">
  <i>"CNNs capture the fine-grained textures, Vision Transformers capture the global context."</i>
</div>
<br />

The system processes input images through two parallel streams. The CNN stream (EfficientNet-B4) preserves spatial locality, while the Transformer stream (ViT) captures long-range dependencies across image patches. These feature vectors are fused using a dynamically learned Attention coefficient ($\alpha$), optimizing the representation for multi-class skin lesion classification.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/skin-cancer-xai/issues).

<div align="center">
  <br/>
  <b>Built with ❤️ <b>
</div>
