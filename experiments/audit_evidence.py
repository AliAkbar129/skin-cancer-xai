"""Independently check published clean metrics and split isolation without images."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score


def audit(directory):
    root = Path(directory)
    report = json.loads((root / 'evaluation.json').read_text())
    manifest = pd.read_csv(root / 'split_manifest.csv.gz')
    predictions = pd.read_csv(root / 'test_predictions.csv.gz')
    assert manifest.image_id.is_unique, 'Duplicate image identifiers'
    assert manifest.groupby('lesion_id').split.nunique().max() == 1, 'Lesion leakage'
    assert manifest.groupby('image_sha256').split.nunique().max() == 1, 'Byte-duplicate leakage'
    expected = manifest[manifest.split == 'test']
    assert predictions.image_id.is_unique
    assert set(predictions.image_id) == set(expected.image_id), 'Incomplete test predictions'
    paired = predictions.merge(expected, on='image_id', suffixes=('', '_manifest'), validate='one_to_one')
    assert (paired.dx == paired.dx_manifest).all()
    assert (paired.lesion_id == paired.lesion_id_manifest).all()
    labels = report['clean_calibrated']['labels']
    probabilities = predictions[['p_' + name for name in labels]].to_numpy()
    assert np.isfinite(probabilities).all()
    assert ((probabilities >= 0) & (probabilities <= 1)).all()
    assert np.allclose(probabilities.sum(axis=1), 1)
    predicted = np.asarray(labels)[probabilities.argmax(axis=1)]
    score = f1_score(predictions.dx, predicted, labels=labels, average='macro', zero_division=0)
    assert np.isclose(score, report['clean_calibrated']['macro_f1']), 'Metric mismatch'
    return {'test_images': len(predictions), 'test_lesions': predictions.lesion_id.nunique(),
            'recomputed_macro_f1': score, 'lesion_and_byte_split_isolation': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()
    print(json.dumps(audit(args.directory), indent=2))
