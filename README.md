# DermoAI Reliability Lab

An early research workbench for image classification, calibration and selective prediction. **Not a medical device, diagnostic service, or completed validation study.** No trained skin-lesion checkpoint or performance claim is bundled.

## What works in this branch

- CPU baseline training from a local HAM10000 metadata/images directory.
- Lesion-grouped train/validation/calibration/test splits and byte-duplicate leakage checks.
- RGB/gradient features with logistic regression, validation-selected regularization, held-out temperature scaling, and a prespecified 0.8 confidence threshold.
- Measured clean/blur/brightness evaluation, calibration error, confusion matrices and risk/coverage curves.
- FastAPI inference gated on a locally trained research artifact; absent or fixture artifacts do not produce disease predictions.
- React evidence dashboard and image upload with explicit errors. Fabricated accuracy, clinician identities, patient counts and mock explanation images were removed from the active application.

The previous hybrid CNN/ViT architecture and XAI experiments remain in source for future work but are **not the active evaluated model**. This first baseline is intentionally simpler and is not claimed to be state of the art.

## Local setup (Python 3.12, Node)

```bash
cd backend
python -m venv .venv
# Activate .venv for your shell first.
python -m pip install -r requirements-research.txt
python -m pytest -q tests
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Open http://localhost:5173. The initial screen correctly reports that training is required. Set `VITE_API_URL` for a different backend. Keep this unauthenticated research application on localhost.

## Train on your own licensed dataset copy

Original dataset: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T . Review its terms and obtain access yourself; no data is redistributed here.

From backend:

```bash
python train.py --metadata /path/HAM10000_metadata.csv --images /path/images --output artifacts --data-mode HAM10000
```

The command produces `baseline.joblib`, `split_manifest.csv` and `evaluation.json`. The server uses `artifacts/baseline.joblib` by default; override `DERMO_MODEL_PATH` if needed. Only load trusted locally generated joblib files. Do not upload pickle/joblib files or commit the dataset/weights to Git.

## Evaluation contract

Splits approximate 60/15/10/15 percent by lesion groups, stratified on diagnosis. Preprocessing learns only from training. Regularization is selected on model-validation data. Temperature is fitted only on calibration data. Test images never tune model, temperature or threshold. Image degradations are prespecified stress tests, not independent clinical external validation. Lesion-disjoint does not mean patient-disjoint when patient identifiers are unavailable.

`--data-mode synthetic_fixture` exists for engineering smoke tests; such artifacts are refused by the inference API. Passing smoke tests does not validate medical performance. The complete training path is exercised on labelled synthetic images by `test_training_smoke.py`.

## Remaining work

Real HAM10000 training and review; compact pretrained CNN and hybrid comparison; uncertainty intervals; external validation; properly evaluated explanations; persistent multiuser experiment storage; deployment hardening. There are no clinical or scholarship guarantees.

## Attribution and status

This branch extends the original AliAkbar129 project with AI-assisted implementation. The owner should review and understand all code before describing it as personal work. NumPy, SciPy, scikit-learn, pandas, Pillow, FastAPI and the existing frontend dependencies retain their respective licenses. No new repository-wide license is asserted. See `docs/STATUS.md` for validation boundaries.
