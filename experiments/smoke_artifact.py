"""Exercise a trusted trained artifact through the API with an engineering fixture."""
import argparse
import io
import json
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument('artifact')
parser.add_argument('--output', required=True)
args = parser.parse_args()
os.environ['DERMO_MODEL_PATH'] = str(Path(args.artifact).resolve())
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from PIL import Image
from fastapi.testclient import TestClient
from main import app

with TestClient(app) as client:
    status = client.get('/model/status').json()
    assert status['ready'], status
    buffer = io.BytesIO()
    Image.new('RGB', (128, 128), (120, 80, 60)).save(buffer, format='PNG')
    result = client.post('/analyze', files={'file': ('engineering-fixture.png', buffer.getvalue(), 'image/png')})
    assert result.status_code == 200, result.text
    value = result.json()
    assert abs(sum(value['all_probabilities'].values()) - 1) < 1e-8
    assert value['model_version'] == status['sha256']
    bad = client.post('/analyze', files={'file': ('bad.png', b'not an image', 'image/png')})
    assert bad.status_code == 422
    report = {'passed': True, 'model_type': value['model_type'], 'artifact_sha256': status['sha256'],
              'checks': ['readiness', 'inference', 'normalized probabilities', 'artifact identity', 'invalid image rejection'],
              'scope': 'Generated engineering fixture only; not medical performance evaluation'}
    Path(args.output).write_text(json.dumps(report, indent=2))
    print(json.dumps(report))
