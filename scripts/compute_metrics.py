#!/usr/bin/env python3
import argparse, json, os, re
import pandas as pd
import numpy as np
from typing import Dict, Any

LABELS = ["FABRICATION","ADMISSION","SILENT_REFUSAL","NULL"]

def extract_counts(d: Dict[str,Any]) -> Dict[str,int]:
    """Try multiple known shapes for counts."""
    # Common keys we've seen in different exporters
    candidates = [
        "labels",                 # {FABRICATION: x, ...} - our actual format!
        "counts",                 
        "label_counts",
        "label_distribution",
        "response_counts",
    ]
    raw = None
    for k in candidates:
        if isinstance(d.get(k), dict):
            raw = d[k]
            break
    
    if raw is None:
        return {lab: 0 for lab in LABELS}

    # Normalize keys to our canonical labels (case-insensitive, underscores/dashes tolerant)
    norm = {}
    for k,v in raw.items():
        kk = str(k).strip().upper().replace(" ", "_").replace("-", "_")
        # tolerate "SILENTREFUSAL" or "REFUSAL" → SILENT_REFUSAL; "ADM" → ADMISSION, etc.
        if "FAB" in kk: norm_key = "FABRICATION"
        elif "ADM" in kk: norm_key = "ADMISSION"
        elif "SILENT" in kk or (kk=="REFUSAL" or "REFUSAL" in kk): norm_key = "SILENT_REFUSAL"
        elif "NULL" in kk: norm_key = "NULL"
        else: 
            # Exact match fallback
            if kk in LABELS:
                norm_key = kk
            else:
                continue
        norm[norm_key] = int(v)
    
    # fill missing
    for lab in LABELS:
        norm.setdefault(lab, 0)
    return norm

def infer_domain_from_filename(filename: str) -> str:
    """Derive domain/study type from filename."""
    fn = os.path.basename(filename)
    if fn.startswith("cross_domain"): 
        return "cross_domain"
    elif fn.startswith("persistence"): 
        return "persistence"
    return "unknown"

def extract_n(d: Dict[str,Any], counts: Dict[str,int]) -> int:
    """Prefer explicit 'n' or 'total' if present; otherwise sum of counts."""
    n = d.get("n") or d.get("total")
    if n is None:
        n = sum(int(v) for v in counts.values()) if counts else 0
    return int(n)

def main(in_dir, out_csv):
    rows = []
    
    for fn in os.listdir(in_dir):
        if not fn.endswith("_stats.json"): 
            continue
        
        fp = os.path.join(in_dir, fn)
        try:
            with open(fp, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not parse {fn}: {e}")
            continue
        
        domain = infer_domain_from_filename(fn)
        
        # Check if this has a by_model structure
        if "by_model" in data and isinstance(data["by_model"], dict):
            # Nested structure: iterate through each model
            for model_name, model_data in data["by_model"].items():
                counts = extract_counts(model_data)
                n = extract_n(model_data, counts)
                
                row = {
                    "file": fn, 
                    "model": model_name, 
                    "domain": domain, 
                    "n": n
                }
                for lab in LABELS:
                    row[f"count_{lab}"] = counts.get(lab, 0)
                rows.append(row)
        else:
            # Flat structure: single model per file
            counts = extract_counts(data)
            model = data.get("model") or data.get("model_name") or "unknown"
            n = extract_n(data, counts)
            
            row = {
                "file": fn, 
                "model": model, 
                "domain": domain, 
                "n": n
            }
            for lab in LABELS:
                row[f"count_{lab}"] = counts.get(lab, 0)
            rows.append(row)
    
    if not rows:
        print(f"Warning: No valid stats files found in {in_dir}")
        # Create empty dataframe with expected columns
        df = pd.DataFrame(columns=["file", "model", "domain", "n"] + 
                                  [f"count_{l}" for l in LABELS] + 
                                  [f"pct_{l}" for l in LABELS])
    else:
        df = pd.DataFrame(rows).sort_values(["model","domain","file"])
        
        # Calculate percentages
        for lab in LABELS:
            df[f"pct_{lab}"] = np.where(
                df["n"].astype(float) > 0, 
                df[f"count_{lab}"] / df["n"], 
                np.nan
            )
    
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} with {len(df)} rows.")
    if len(df) > 0:
        print(f"Models found: {df['model'].unique().tolist()}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()
    main(args.in_dir, args.out_csv)
