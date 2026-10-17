"""Local research API; untrained models never return diagnoses."""
import io, os, hashlib
from pathlib import Path
import joblib
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from reliability import image_features, calibrated_probabilities
app=FastAPI(title='DermoAI Reliability Lab',version='0.2.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_methods=['GET','POST'],allow_headers=['Content-Type'])
MAX_BYTES=5*1024*1024
Image.MAX_IMAGE_PIXELS=16_000_000

def load_artifact():
    path=Path(os.environ.get('DERMO_MODEL_PATH','artifacts/baseline.joblib'))
    if not path.is_file(): raise HTTPException(503,'No trained model installed. Run the documented dataset training pipeline first.')
    # Trust only local artifacts you generated; never accept uploaded joblib/pickle.
    artifact=joblib.load(path)
    if artifact.get('schema_version')!=1 or artifact.get('data_mode')!='HAM10000':
        raise HTTPException(503,'Not a HAM10000 research artifact. Fixture models cannot serve analyses.')
    return artifact,hashlib.sha256(path.read_bytes()).hexdigest()

@app.get('/health')
def health(): return {'status':'alive','purpose':'research_only'}

@app.get('/model/status')
def status():
    try: artifact,digest=load_artifact()
    except HTTPException as exc: return {'ready':False,'reason':exc.detail,'metrics':None}
    return {'ready':True,'model_type':artifact['model_type'],'sha256':digest,'data_mode':artifact['data_mode'],
            'metrics':artifact['metrics'],'threshold':artifact['threshold'],'temperature':artifact['temperature'],
            'limitations':'Color/texture baseline; not clinical validation or a CNN comparison.'}

@app.post('/analyze')
async def analyze(file: UploadFile=File(...)):
    artifact,digest=load_artifact()
    raw=await file.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES: raise HTTPException(413,'Maximum upload size is 5 MiB.')
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format not in {'PNG','JPEG'} or im.width*im.height>16_000_000: raise ValueError('Unsupported image')
            image=im.convert('RGB')
    except (UnidentifiedImageError,OSError,ValueError,Image.DecompressionBombError):
        raise HTTPException(422,'Invalid or oversized JPEG/PNG image.')
    probs=calibrated_probabilities(artifact['pipeline'].predict_proba(image_features(image)[None,:]),artifact['temperature'])[0]
    labels=artifact['pipeline'].classes_.tolist(); best=int(probs.argmax())
    return {'prediction':labels[best],'probability':float(probs[best]),'all_probabilities':dict(zip(labels,probs.tolist())),
            'decision':'refer' if probs[best]<artifact['threshold'] else 'accept','model_version':digest,
            'data_mode':artifact['data_mode'],'model_type':artifact['model_type'],'xai':{},
            'notice':'Research only. Input domain and clinical reliability are not validated.'}
