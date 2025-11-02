#!/usr/bin/env python3
import argparse, os
import pandas as pd
import matplotlib.pyplot as plt

def main(tables_csv, figdir):
    os.makedirs(figdir, exist_ok=True)
    df = pd.read_csv(tables_csv)
    agg = df.groupby("model").sum(numeric_only=True)
    agg["n"] = agg[[c for c in agg.columns if c.startswith("count_")]].sum(axis=1)
    parts = ["FABRICATION","ADMISSION","SILENT_REFUSAL","NULL"]
    pct = agg[[f"count_{p}" for p in parts]].div(agg["n"], axis=0)

    ax = pct.plot(kind="bar", figsize=(8,5))
    ax.set_ylabel("Proportion")
    ax.set_xlabel("Model")
    ax.set_title("Cross-Domain Response Distribution")
    ax.legend([p.replace("_"," ").title() for p in parts], bbox_to_anchor=(1.02,1), loc="upper left")
    plt.tight_layout()
    out = os.path.join(figdir, "figure1_cross_domain.png")
    plt.savefig(out, dpi=200)
    print(f"Saved {out}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables_csv", required=True)
    ap.add_argument("--figdir", required=True)
    args = ap.parse_args()
    main(args.tables_csv, args.figdir)
