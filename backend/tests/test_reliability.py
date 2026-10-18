import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from reliability import grouped_split,metrics,calibrated_probabilities,fit_temperature
from main import app

def test_groups_do_not_cross_partitions():
    rows=[{'image_id':f'{c}-{i}-{v}','lesion_id':f'{c}-{i}','dx':c} for c in ['mel','nv'] for i in range(100) for v in range(2)]
    out=grouped_split(pd.DataFrame(rows))
    assert out.groupby('lesion_id').split.nunique().max()==1
    assert set(out.split)=={'train','validation','calibration','test'}

def test_duplicate_identifiers_rejected():
    with pytest.raises(ValueError): grouped_split(pd.DataFrame([{'image_id':'a','lesion_id':'x','dx':'mel'}]*2))

def test_conflicting_lesion_labels_rejected():
    with pytest.raises(ValueError): grouped_split(pd.DataFrame([{'image_id':'a','lesion_id':'x','dx':'mel'},{'image_id':'b','lesion_id':'x','dx':'nv'}]))

def test_all_refer_is_not_zero_error():
    result=metrics([[.6,.4],[.4,.6]],[0,1],['a','b'],.9)
    assert result['coverage']==0 and result['accepted_error'] is None

def test_perfect_predictions_and_ece_boundary():
    result=metrics([[1,0],[0,1]],[0,1],['a','b'],.5)
    assert result['macro_f1']==1 and result['ece_10_equal_width_bins']<1e-9

def test_temperature_and_probability_validation():
    p=np.array([[.9,.1],[.9,.1],[.1,.9],[.1,.9]])
    t=fit_temperature(p,[0,1,0,1]); q=calibrated_probabilities(p,t)
    assert t>1 and np.allclose(q.sum(1),1)
    with pytest.raises(ValueError): calibrated_probabilities([[np.nan,1]])

def test_missing_model_never_predicts(monkeypatch,tmp_path):
    monkeypatch.setenv('DERMO_MODEL_PATH',str(tmp_path/'absent'))
    client=TestClient(app)
    assert client.get('/model/status').json()['ready'] is False
    response=client.post('/analyze',files={'file':('x.jpg',b'invalid','image/jpeg')})
    assert response.status_code==503 and 'prediction' not in response.json()
