# Interrater Reliability Report

## Dataset
- File: irr/irr_human.csv
- Items: 100
- Labels present: ADMISSION, FABRICATION, SILENT_REFUSAL

## Agreement
- Percent agreement: **100.0%** (100/100)
- Cohen's kappa: **1.000** 95% CI [1.000, 1.000]

## Per label agreement rate (share of all items)

| Label | Agreement share |
|---|---|
| ADMISSION | 63.0% |
| FABRICATION | 18.0% |
| SILENT_REFUSAL | 19.0% |

## Confusion matrix (rows = Rater A, cols = Rater B)

| | ADMISSION | FABRICATION | SILENT_REFUSAL |
|---|---|---|---|
| ADMISSION | 63 | 0 | 0 |
| FABRICATION | 0 | 18 | 0 |
| SILENT_REFUSAL | 0 | 0 | 19 |

## Command
Computed by irr/compute_irr.py
