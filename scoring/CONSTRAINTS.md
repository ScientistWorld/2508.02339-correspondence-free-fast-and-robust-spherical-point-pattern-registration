# Scientist Constraints

## Problem Formulation
The scientist must work on the spherical point pattern registration problem (rotation estimation between two sets of 3D unit vectors without correspondences). The evaluation uses the synthetic "Robust Vector Alignment Dataset" with 5 patterns, 7 outlier configurations, and 100 rotations.

## Data
The scientist must use the paper's released dataset under `method/paper_code/vector_alignment_dataset/` through the loader in `data/dataset.py` — all 5 patterns (A1–A5), all 7 configurations (B1–B7), all 100 rotations. No external data may be substituted for the core evaluation.

## Evaluation Protocol
Rotational angular error must be measured as: arccos((trace(R_true^T * R_est) - 1) / 2) in degrees. The same error metric and dataset must be used for all comparisons.

## Allowed Modifications
The scientist may:
- Modify or replace the registration algorithms (SPMC, FRS, SPMC+FRS)
- Change histogram resolution, correlation method, or iteration strategy
- Add preprocessing or postprocessing steps
- Use different spherical embeddings

## Prohibited Modifications
- Using correspondences between points (the paper's contribution is correspondence-free)
- Hardcoding known ground-truth rotations
- Training on the evaluation rotations

## Compliance Checklist
- [ ] Rotation error metric uses the geodesic distance formula above
- [ ] All experiments use the released Robust Vector Alignment Dataset
- [ ] No correspondences between source and template points are used
- [ ] Timing is measured on the same dataset as accuracy
