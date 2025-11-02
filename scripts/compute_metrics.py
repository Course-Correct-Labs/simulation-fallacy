#!/usr/bin/env python3
import argparse, json, os
import pandas as pd
import numpy as np

LABELS = ["FABRICATION","ADMISSION","SILENT_REFUSAL","NULL"]

def main(in_dir, out_csv):
    rows = []
    for fn in os.listdir(in_dir):
        if fn.endswith("_stats.json"):
            with open(os.path.join(in_dir, fn),'r') as f:
                d = json.load(f)
            row = {
                "model": d.get("model","unknown"),
                "domain": d.get("domain","unknown"),
                "n": d.get("n", np.nan)
            }
            counts = d.get("counts",{})
            for lab in LABELS:
                row[f"count_{lab}"] = counts.get(lab,0)
            rows.append(row)
    df = pd.DataFrame(rows).sort_values(["model","domain"])
    for lab in LABELS:
        df[f"pct_{lab}"] = np.where(df["n"].astype(float)>0, df[f"count_{lab}"]/df["n"], np.nan)
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} with {len(df)} rows.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()
    main(args.in_dir, args.out_csv)
