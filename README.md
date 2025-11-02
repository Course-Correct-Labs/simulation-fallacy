# Simulation Fallacy Benchmark

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Course-Correct-Labs/simulation-fallacy/blob/main/notebooks/Simulation_Fallacy_Reproduction.ipynb)

A reproducible benchmark and analysis toolkit for evaluating *epistemic boundary behavior* of LLMs when tool access is **absent but implied** (the *Simulation Fallacy* condition).

**Core findings (paper):**
- GPT-5: ~98% silent refusal
- Gemini 2.5 Pro: ~81% fabrication
- Claude Sonnet 4: admission/fabrication oscillation

Companion to *The Mirror Loop* (arXiv:2510.21861). Part of Course Correct Labs' epistemic reliability program.

## Repo structure
- `results/final/` — final JSON and *_stats.json outputs
- `figures/` — generated figures
- `scripts/` — minimal analysis
- `notebooks/` — Colab notebook
- `prompts/` — prompt templates (add any missing ones you used)

## Quickstart (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/compute_metrics.py --in_dir results/final --out_csv results/final/label_counts_with_pct.csv
python scripts/plot_figures.py --tables_csv results/final/label_counts_with_pct.csv --figdir figures
```

## Quickstart (Colab)

Open the badge above and Run all.

## Data

We include the final canonical artifacts used in the paper under `results/final/`. Replace with your own runs to re-evaluate.

## Citation

See CITATION.cff.
