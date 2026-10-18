# Implementation and evidence status

The full 10,015-image HAM10000 handcrafted baseline completed on GitHub Actions. Published evidence includes lesion splits, image hashes, test probabilities, uncertainty intervals, calibration, class-level coverage, and blur/brightness stress results. See the README for measured values and the original workflow link.

The frozen ResNet18 comparison is still running at this publication. Its architecture was chosen after viewing handcrafted test results, so it is exploratory. No claim of hybrid CNN/ViT reproduction, validated explanation quality, clinical suitability, or novel algorithm is made.

The reliability baseline CI passes. A separately downloaded trained artifact passed API readiness, inference probability normalization and invalid-image rejection using a generated engineering fixture. This tests integration, not classification accuracy.

The application remains a localhost research workbench without authentication, persisted experiments or a true background worker. Joblib artifacts must be trusted. No patient-disjoint guarantee is possible without patient identifiers. Lighting shift causes severe confident errors; clean calibration does not establish out-of-distribution reliability. Full clinical/external evaluation and deployment hardening remain unfinished.
