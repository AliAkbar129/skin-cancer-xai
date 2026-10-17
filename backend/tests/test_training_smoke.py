"""Synthetic fixture smoke test, explicitly not medical validation."""
import numpy as np,pandas as pd,joblib
from PIL import Image
from train import run
from main import app
from fastapi.testclient import TestClient

def test_complete_training_and_fixture_rejection(tmp_path,monkeypatch):
    rng=np.random.default_rng(9);images=tmp_path/'images';images.mkdir();rows=[]
    for label,base in [('mel',80),('nv',170)]:
        for i in range(60):
            identifier=f'{label}-{i}';a=np.clip(rng.normal(base,20,(20,20,3)),0,255).astype('uint8')
            Image.fromarray(a).save(images/(identifier+'.jpg'));rows.append({'image_id':identifier,'lesion_id':identifier,'dx':label})
    meta=tmp_path/'metadata.csv';pd.DataFrame(rows).to_csv(meta,index=False);out=tmp_path/'artifacts'
    run(meta,images,out,data_mode='synthetic_fixture')
    artifact=joblib.load(out/'baseline.joblib');assert artifact['data_mode']=='synthetic_fixture'
    assert (out/'evaluation.json').is_file() and artifact['metrics']['clean_calibrated']['n']>0
    monkeypatch.setenv('DERMO_MODEL_PATH',str(out/'baseline.joblib'))
    assert TestClient(app).get('/model/status').json()['ready'] is False
