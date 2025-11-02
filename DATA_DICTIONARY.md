# Data Dictionary

This document describes the structure and fields of all JSON files in `results/final/`.

## File Naming Convention

- `{study_type}_v{version}_{timestamp}.json` — Full per-sample results
- `{study_type}_v{version}_{timestamp}_stats.json` — Aggregated statistics

Study types:
- `cross_domain` — Single-turn responses across different tool-absence conditions (web, image, database, file)
- `persistence` — Multi-turn (3 turns) to measure label stability over repeated queries

## Stats Files (`*_stats.json`)

Aggregated model-level statistics.

### Top-level Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_responses` | int | Total number of responses across all models |
| `total_calls` | int | Total API calls made (may include retries) |
| `by_model` | object | Statistics grouped by model identifier |

### `by_model[model_name]` Object

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total responses for this model |
| `labels` | object | Raw counts per label (FABRICATION, ADMISSION, SILENT_REFUSAL, NULL) |
| `rates` | object | Proportions (0–1) for each label |
| `cis_wilson_95` | object | 95% confidence intervals (Wilson score) for each label |
| `cis_wilson_95[label].lo` | float | Lower bound of 95% CI |
| `cis_wilson_95[label].hi` | float | Upper bound of 95% CI |
| `blame_rate` | float | Proportion of responses that contain blame language (deprecated/optional) |
| `cost_usd` | float | Total cost in USD for this model's API calls |

### Label Taxonomy

| Label | Description |
|-------|-------------|
| `FABRICATION` | Model generates plausible but false output (hallucination under tool absence) |
| `ADMISSION` | Model explicitly states it cannot perform the task |
| `SILENT_REFUSAL` | Model returns structured refusal (e.g., `null` values, empty fields) without explanation |
| `NULL` | Ambiguous or unclassifiable response |

## Full Result Files (`*.json` without `_stats`)

Per-sample results with full response data.

### Top-level Structure

```json
{
  "config": { ... },
  "results": { "model_name": [ ... ] },
  "total_spend": float,
  "elapsed": float,
  "completed": timestamp
}
```

### `config` Object

| Field | Type | Description |
|-------|------|-------------|
| `budget_usd_cap` | float | Maximum budget allowed for the run |
| `conditions` | array | List of experimental conditions (tool-absence scenarios) |
| `conditions[i].id` | string | Condition identifier (e.g., `no_web_search`) |
| `conditions[i].template` | string | Prompt template filename used |
| `models` | array | List of models tested |
| `models[i].model` | string | Model identifier (e.g., `gpt-5`) |
| `models[i].provider` | string | Provider name (`openai`, `anthropic`, `google`) |
| `max_completion_tokens_*` | int | Max tokens per completion (provider-specific) |

### `results[model_name]` Array

Each element is a single API call result:

| Field | Type | Description |
|-------|------|-------------|
| `dedupe_key` | string | SHA256 hash identifying unique prompt+condition+seed combinations |
| `provider` | string | API provider (`openai`, `anthropic`, `google`) |
| `model` | string | Full model identifier |
| `condition_id` | string | Experimental condition ID (links to `config.conditions`) |
| `seed` | int | Random seed for this sample (for reproducibility) |
| `turn_index` | int | Turn number (0-indexed; only multi-turn in `persistence` study) |
| `success` | bool | Whether API call succeeded |
| `classification` | string | Human/automated label (FABRICATION, ADMISSION, SILENT_REFUSAL, NULL) |
| `response_content` | string | Raw model response (may be JSON, text, or structured output) |
| `tokens_prompt` | int | Input tokens used |
| `tokens_completion` | int | Output tokens generated |
| `cost_usd` | float | Cost of this individual call |
| `timestamp` | string | ISO 8601 timestamp of API call |

### Multi-turn Sequences (Persistence Study Only)

Responses with the same `dedupe_key` form a sequence. Use `turn_index` to order them chronologically. The `persistence` study has 3 turns per sequence (turn 0, 1, 2).

**Transition matrices** are computed from pairs `(classification[turn_N], classification[turn_N+1])` within each sequence.

## Inter-Rater Reliability Files

| File | Description |
|------|-------------|
| `irr_clean.csv` | Human-labeled subset for IRR validation |
| `irr_confusion_matrix.csv` | Agreement matrix between two raters |
| `irr_report.md` | Cohen's κ and agreement statistics |

Columns in `irr_clean.csv`:
- `sample_id` — Unique identifier
- `model` — Model tested
- `condition_id` — Experimental condition
- `response_content` — Model output
- `rater_1` — Label assigned by first rater
- `rater_2` — Label assigned by second rater
- `consensus` — Final agreed label (used in main analysis)

## Reproducibility Notes

- All `dedupe_key` values are deterministic: changing the prompt, condition, or seed will produce a different hash.
- `turn_index` is always `0` for single-turn studies (`cross_domain`).
- Cost estimates are based on provider-reported token counts at time of execution (rates may change).

## Questions?

Open an issue at [github.com/Course-Correct-Labs/simulation-fallacy](https://github.com/Course-Correct-Labs/simulation-fallacy).
