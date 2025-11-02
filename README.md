# Simulation Fallacy Benchmark

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Course-Correct-Labs/simulation-fallacy/blob/main/notebooks/Simulation_Fallacy_Reproduction.ipynb)

A reproducible benchmark and analysis toolkit for evaluating *epistemic boundary behavior* of LLMs when tool access is **absent but implied** (the *Simulation Fallacy* condition).

**Core findings (paper):**
- **GPT-5**: ~98% silent refusal (epistemic boundary respected)
- **Gemini 2.5 Pro**: ~81% fabrication (high confabulation rate)
- **Claude Sonnet 4**: admission/fabrication oscillation (inconsistent boundary behavior)

Companion to *The Mirror Loop* ([arXiv:2510.21861](https://arxiv.org/abs/2510.21861)). Part of Course Correct Labs' epistemic reliability program.

---

## Repository Structure

```
simulation-fallacy/
│
├── results/final/          # Final JSON outputs and stats (8 files + 3 IRR artifacts)
├── figures/                # Generated figures (Figure 1 & 2)
├── scripts/                # Minimal analysis scripts
│   ├── compute_metrics.py  # Label counts and percentages
│   ├── plot_figures.py     # Cross-domain distribution (Figure 1)
│   └── plot_transitions.py # Turn-by-turn dynamics (Figure 2)
├── notebooks/              # Colab-ready reproduction notebook
├── prompts/                # Exact prompt templates used in study (11 .txt files)
├── DATA_DICTIONARY.md      # Schema and field definitions
├── CITATION.cff            # Citation metadata
└── README.md               # This file
```

---

## Quickstart (Local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Compute label distributions
python scripts/compute_metrics.py \
  --in_dir results/final \
  --out_csv results/final/label_counts_with_pct.csv

# Regenerate Figure 1: Cross-domain response distribution
python scripts/plot_figures.py \
  --tables_csv results/final/label_counts_with_pct.csv \
  --figdir figures

# Regenerate Figure 2: Transition matrices
python scripts/plot_transitions.py \
  --in_dir results/final \
  --figdir figures
```

---

## Quickstart (Colab)

Click the badge above and **Run all**. The notebook will:
1. Clone this repository
2. Install dependencies
3. Compute metrics and regenerate both figures
4. Display the results inline

---

## Figures

### Figure 1: Cross-Domain Response Distribution
**File:** `figures/figure1_cross_domain.png`  
**Description:** Model-level label distributions (FABRICATION, ADMISSION, SILENT_REFUSAL, NULL) across all tool-absence conditions (web search, image reference, database schema, file access).  
**Reproduces:** Run `scripts/plot_figures.py`

### Figure 2: Turn-by-Turn Transition Dynamics
**File:** `figures/figure2_transition_matrices.png`  
**Description:** Transition probability matrices showing how labels change across consecutive turns in the persistence study (3-turn sequences).  
**Reproduces:** Run `scripts/plot_transitions.py`

---

## Data

We include the final canonical artifacts used in the paper under `results/final/`:

- **Cross-domain study** (single-turn):
  - `cross_domain_v1_20251030_183025.json` + `_stats.json`
  - `cross_domain_v1_anthropic_catchup_20251030_233401.json` + `_stats.json`

- **Persistence study** (3-turn sequences):
  - `persistence_v1_20251030_190503.json` + `_stats.json`
  - `persistence_v1_anthropic_catchup_20251030_234443.json` + `_stats.json`

- **Inter-rater reliability**:
  - `irr_clean.csv`, `irr_confusion_matrix.csv`, `irr_report.md`

**Schema documentation:** See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for field definitions and data structure.

Replace these files with your own runs to re-evaluate the pipeline.

---

## Reproducibility Checklist

✅ **Data availability**: All final results (JSON, IRR artifacts) are included in `results/final/`  
✅ **Deterministic scripts**: Analysis scripts produce identical output given the same input files  
✅ **Figures regenerate**: Both figures reproduce from the included data (minor matplotlib version differences possible)  
✅ **Prompts published**: Exact prompt templates are in `prompts/` (11 .txt files)  
✅ **IRR artifacts**: Human inter-rater reliability data and reports are provided  
✅ **No secrets**: No API keys, credentials, or proprietary data are included  
✅ **Version pinning**: `requirements.txt` specifies package versions (≥ constraints)  
✅ **Open license**: MIT license for code and artifacts

**Note on LLM non-determinism**: Due to temperature/sampling and API-level variations, re-running the data collection pipeline will produce *similar* but not *identical* results. The published data represents the canonical run used in the paper.

---

## Ethics & Risk Note

- **No real user data**: All prompts are synthetic and designed to test epistemic boundaries, not to elicit harmful content.
- **No secrets or credentials**: This repository contains no API keys, tokens, or proprietary information.
- **Synthetic scenarios**: Prompt templates simulate tool-absence conditions (missing web search, database access, etc.) to measure model behavior under uncertainty.
- **Research purpose**: This benchmark is intended for academic research and model safety evaluation. Findings should not be used to manipulate or mislead users.

---

## Citation

See [`CITATION.cff`](CITATION.cff) for machine-readable citation metadata.

**BibTeX:**
```bibtex
@article{devilling2025simulation,
  title={Simulation Fallacy: How Models Behave When Tool Access Is Missing},
  author={DeVilling, Bentley},
  year={2025},
  url={https://github.com/Course-Correct-Labs/simulation-fallacy}
}
```

---

## Related Work

- [The Mirror Loop](https://arxiv.org/abs/2510.21861) — Semantic drift and novelty dynamics in recursive LLM self-interaction
- [Recursive Confabulation](https://github.com/Course-Correct-Labs/recursive-confabulation) — Multi-turn hallucination persistence benchmark

---

## Questions or Issues?

Open an issue at [github.com/Course-Correct-Labs/simulation-fallacy/issues](https://github.com/Course-Correct-Labs/simulation-fallacy/issues).

---

**License:** MIT  
**Maintained by:** [Course Correct Labs](https://github.com/Course-Correct-Labs)

---

## Troubleshooting Colab

### Issue: Figure 1 shows blank or all zeros

**Symptom:** The notebook runs but `label_counts_with_pct.csv` shows `unknown,unknown` with zero counts.

**Cause:** Colab cloned the repo before the parser fix was committed, or is using cached code.

**Fix:** Run these cells to force-sync to the latest code:

```python
# 1) Hard reset to latest main
%cd /content/simulation-fallacy
!git fetch origin
!git checkout main
!git reset --hard origin/main
!git log -1 --oneline  # Should show commit 1ffd2be or later

# 2) Reinstall dependencies
!pip -q install -r requirements.txt

# 3) Recompute tables
!python scripts/compute_metrics.py --in_dir results/final --out_csv results/final/label_counts_with_pct.csv
!sed -n '1,20p' results/final/label_counts_with_pct.csv
# Expected: 6 rows with real model names (openai/gpt-5, google/gemini-2.5-pro, anthropic/claude-sonnet-4-20250514)

# 4) Regenerate Figure 1
!python scripts/plot_figures.py --tables_csv results/final/label_counts_with_pct.csv --figdir figures
from IPython.display import Image, display
display(Image('figures/figure1_cross_domain.png'))

# 5) Regenerate Figure 2
!python scripts/plot_transitions.py --in_dir results/final --figdir figures
display(Image('figures/figure2_transition_matrices.png'))
```

### Still seeing zeros or blanks?

Check:
- ✅ **Correct commit**: Run `!git log -1 --oneline` and verify hash is `1ffd2be` or later
- ✅ **Correct directory**: Run `!pwd` → should print `/content/simulation-fallacy`
- ✅ **Files present**: Run `!ls -lah results/final` → should show 6 `*_stats.json` files
- ✅ **Nonzero CSV**: Run `!head results/final/label_counts_with_pct.csv` → model column should show real names, not "unknown"

### Issue: "This figure includes Axes that are not compatible with tight_layout"

**Symptom:** Matplotlib warning when generating Figure 2.

**Fix:** This is a harmless warning. The figure still generates correctly. Ignore it or add this to suppress:

```python
import warnings
warnings.filterwarnings('ignore', message='.*tight_layout.*')
```
