"""Post-hoc paired lesion bootstrap; descriptive, not confirmatory inference."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

root = Path(__file__).resolve().parents[1] / 'evidence'
baseline = pd.read_csv(root / 'ham10000/test_predictions.csv.gz').sort_values('image_id').reset_index(drop=True)
neural = pd.read_csv(root / 'resnet18/test_predictions.csv.gz').sort_values('image_id').reset_index(drop=True)
assert baseline[['image_id', 'lesion_id', 'dx']].equals(neural[['image_id', 'lesion_id', 'dx']])
columns = [c for c in baseline if c.startswith('p_')]
labels = np.array([c[2:] for c in columns])
y = baseline.dx.to_numpy()
predictions = [labels[frame[columns].to_numpy().argmax(axis=1)] for frame in (baseline, neural)]
groups = baseline.lesion_id.to_numpy()
unique = np.unique(groups)
indices = {g: np.flatnonzero(groups == g) for g in unique}


def score(predicted, ix):
    return float(f1_score(y[ix], predicted[ix], labels=labels, average='macro', zero_division=0))


all_rows = np.arange(len(y))
delta = score(predictions[1], all_rows) - score(predictions[0], all_rows)
rng = np.random.default_rng(42)
draws = []
for _ in range(1000):
    ix = np.concatenate([indices[g] for g in rng.choice(unique, len(unique), replace=True)])
    draws.append(score(predictions[1], ix) - score(predictions[0], ix))
manifest = pd.read_csv(root / 'ham10000/split_manifest.csv.gz')
majority = manifest.loc[manifest.split == 'train', 'dx'].mode().iloc[0]
report = {
    'analysis': 'Exploratory paired comparison on reused test lesions',
    'seed': 42, 'bootstrap_resamples': 1000, 'test_images': len(y),
    'test_lesions': len(unique), 'majority_label_from_training': majority,
    'majority_reference_macro_f1': score(np.full(len(y), majority), all_rows),
    'frozen_minus_handcrafted_macro_f1': delta,
    'paired_lesion_bootstrap_95_percentile': np.quantile(draws, [.025, .975]).tolist(),
    'limitations': ['Architecture chosen after examining baseline test results',
                   'Same images and lesions; no independent external confirmation',
                   'Interval excludes training-seed and model-selection uncertainty',
                   'Not a claim of clinical benefit or novel algorithm']
}
(root / 'comparison.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
