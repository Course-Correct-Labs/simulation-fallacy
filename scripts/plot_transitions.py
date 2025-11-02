#!/usr/bin/env python3
"""
Compute and plot turn-by-turn transition matrices from persistence study data.
"""
import argparse
import json
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

LABELS = ["FABRICATION", "ADMISSION", "SILENT_REFUSAL", "NULL"]

def load_sequences(json_path):
    """Load and group results by sequence (dedupe_key)."""
    with open(json_path) as f:
        data = json.load(f)
    
    results = data.get("results", {})
    sequences_by_model = {}
    
    for model, items in results.items():
        sequences = defaultdict(list)
        for item in items:
            key = item["dedupe_key"]
            sequences[key].append(item)
        
        # Sort each sequence by turn_index
        for key in sequences:
            sequences[key] = sorted(sequences[key], key=lambda x: x["turn_index"])
        
        sequences_by_model[model] = sequences
    
    return sequences_by_model

def compute_transition_matrix(sequences):
    """Compute transition counts from turn N to turn N+1."""
    transitions = {lab: {lab2: 0 for lab2 in LABELS} for lab in LABELS}
    
    for seq_items in sequences.values():
        for i in range(len(seq_items) - 1):
            from_label = seq_items[i]["classification"]
            to_label = seq_items[i + 1]["classification"]
            if from_label in LABELS and to_label in LABELS:
                transitions[from_label][to_label] += 1
    
    # Convert to numpy array
    matrix = np.zeros((len(LABELS), len(LABELS)))
    for i, from_lab in enumerate(LABELS):
        for j, to_lab in enumerate(LABELS):
            matrix[i, j] = transitions[from_lab][to_lab]
    
    # Normalize by row (convert to probabilities)
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # avoid division by zero
    matrix_norm = matrix / row_sums
    
    return matrix, matrix_norm

def plot_all_transitions(sequences_by_model, figdir):
    """Plot transition matrices for all models."""
    os.makedirs(figdir, exist_ok=True)
    
    n_models = len(sequences_by_model)
    fig, axes = plt.subplots(1, n_models, figsize=(6 * n_models, 5))
    if n_models == 1:
        axes = [axes]
    
    for ax, (model, sequences) in zip(axes, sequences_by_model.items()):
        _, matrix_norm = compute_transition_matrix(sequences)
        
        # Plot heatmap
        im = ax.imshow(matrix_norm, cmap='YlOrRd', vmin=0, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(range(len(LABELS)))
        ax.set_yticks(range(len(LABELS)))
        ax.set_xticklabels([l.replace("_", "\n") for l in LABELS], fontsize=9)
        ax.set_yticklabels([l.replace("_", " ") for l in LABELS], fontsize=9)
        
        # Add values in cells
        for i in range(len(LABELS)):
            for j in range(len(LABELS)):
                val = matrix_norm[i, j]
                text = ax.text(j, i, f"{val:.2f}" if val > 0 else "",
                              ha="center", va="center", color="black" if val < 0.5 else "white",
                              fontsize=8)
        
        # Model name as title
        model_short = model.split("/")[-1]
        ax.set_title(f"{model_short}", fontsize=11, fontweight='bold')
        ax.set_xlabel("Turn N+1", fontsize=10)
        ax.set_ylabel("Turn N", fontsize=10)
    
    # Add colorbar
    fig.colorbar(im, ax=axes, fraction=0.02, pad=0.04, label="Transition Probability")
    
    plt.suptitle("Turn-by-Turn Transition Dynamics (Persistence Study)", fontsize=13, fontweight='bold')
    plt.tight_layout()
    
    out_path = os.path.join(figdir, "figure2_transition_matrices.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    print(f"Saved {out_path}")

def main(in_dir, figdir):
    # Find persistence JSON files
    persistence_files = [
        f for f in os.listdir(in_dir)
        if f.startswith("persistence_") and f.endswith(".json") and "_stats" not in f
    ]
    
    if not persistence_files:
        print(f"Warning: No persistence JSON files found in {in_dir}")
        return
    
    # Use the first persistence file (or merge multiple if needed)
    json_path = os.path.join(in_dir, persistence_files[0])
    print(f"Loading sequences from {json_path}")
    
    sequences_by_model = load_sequences(json_path)
    print(f"Found {len(sequences_by_model)} models")
    
    for model, seqs in sequences_by_model.items():
        print(f"  {model}: {len(seqs)} sequences")
    
    plot_all_transitions(sequences_by_model, figdir)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", required=True, help="Directory with persistence JSON files")
    ap.add_argument("--figdir", required=True, help="Output directory for figures")
    args = ap.parse_args()
    main(args.in_dir, args.figdir)
