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
import warnings

# Suppress tight_layout warning
warnings.filterwarnings('ignore', message='.*tight_layout.*')

LABELS = ["FABRICATION", "ADMISSION", "SILENT_REFUSAL", "NULL"]

def canonicalize_label(label):
    """Normalize label strings to canonical form."""
    if label is None:
        return None
    
    s = str(label).strip().upper().replace(" ", "_").replace("-", "_")
    
    # Map variations to canonical labels
    if "FAB" in s or "HALLUCIN" in s:
        return "FABRICATION"
    elif "ADM" in s or "ADMIT" in s:
        return "ADMISSION"
    elif "SILENT" in s or (s in ("REF", "REFUSAL", "SILENTREFUSAL")):
        return "SILENT_REFUSAL"
    elif "NULL" in s or s in ("NONE", "EMPTY"):
        return "NULL"
    elif s in LABELS:
        return s
    else:
        return None

def load_sequences(json_path):
    """
    Load and group results by sequence.
    In persistence studies, turns have DIFFERENT dedupe_keys but share (condition_id, seed).
    """
    with open(json_path) as f:
        data = json.load(f)
    
    if "results" in data and isinstance(data["results"], dict):
        results = data["results"]
    else:
        results = {"unknown": data.get("items", [])}
    
    sequences_by_model = {}
    
    for model, items in results.items():
        if not isinstance(items, list):
            continue
        
        sequences = defaultdict(list)
        
        for item in items:
            # Group by (condition_id, seed) for multi-turn sequences
            condition = item.get("condition_id", "default")
            seed = item.get("seed", 0)
            seq_key = f"{condition}_{seed}"
            
            label = item.get("classification") or item.get("label") or item.get("state")
            canonical_label = canonicalize_label(label)
            
            if canonical_label:
                sequences[seq_key].append({
                    "turn_index": item.get("turn_index", 0),
                    "label": canonical_label
                })
        
        # Sort each sequence by turn_index
        for key in sequences:
            sequences[key] = sorted(sequences[key], key=lambda x: x["turn_index"])
        
        if sequences:
            sequences_by_model[model] = sequences
    
    return sequences_by_model

def compute_transition_matrix(sequences):
    """Compute transition counts from turn N to turn N+1."""
    transitions = {lab: {lab2: 0 for lab2 in LABELS} for lab in LABELS}
    
    for seq_items in sequences.values():
        if len(seq_items) < 2:
            continue
        
        for i in range(len(seq_items) - 1):
            from_label = seq_items[i]["label"]
            to_label = seq_items[i + 1]["label"]
            
            if from_label in LABELS and to_label in LABELS:
                transitions[from_label][to_label] += 1
    
    # Convert to numpy array
    matrix = np.zeros((len(LABELS), len(LABELS)))
    for i, from_lab in enumerate(LABELS):
        for j, to_lab in enumerate(LABELS):
            matrix[i, j] = transitions[from_lab][to_lab]
    
    # Normalize by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        matrix_norm = np.where(row_sums > 0, matrix / row_sums, 0.0)
    
    return matrix, matrix_norm

def plot_all_transitions(sequences_by_model, figdir):
    """Plot transition matrices for all models."""
    os.makedirs(figdir, exist_ok=True)
    
    n_models = len(sequences_by_model)
    if n_models == 0:
        print("Warning: No models found with valid sequences")
        return
    
    cols = min(3, n_models)
    rows = (n_models + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
    
    if n_models == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if hasattr(axes, 'flatten') else axes
    
    for idx, (model, sequences) in enumerate(sequences_by_model.items()):
        ax = axes[idx]
        _, matrix_norm = compute_transition_matrix(sequences)
        
        im = ax.imshow(matrix_norm, cmap='YlOrRd', vmin=0, vmax=1)
        
        ax.set_xticks(range(len(LABELS)))
        ax.set_yticks(range(len(LABELS)))
        ax.set_xticklabels([l.replace("_", "\n") for l in LABELS], fontsize=9)
        ax.set_yticklabels([l.replace("_", " ") for l in LABELS], fontsize=9)
        
        # Add values in cells
        for i in range(len(LABELS)):
            for j in range(len(LABELS)):
                val = matrix_norm[i, j]
                if val > 0.01:
                    text = ax.text(j, i, f"{val:.2f}",
                                  ha="center", va="center", 
                                  color="white" if val > 0.5 else "black",
                                  fontsize=10, fontweight='bold')
        
        model_short = model.split("/")[-1] if "/" in model else model
        ax.set_title(f"{model_short}", fontsize=11, fontweight='bold')
        ax.set_xlabel("Turn N+1", fontsize=10)
        ax.set_ylabel("Turn N", fontsize=10)
    
    # Hide unused subplots
    for idx in range(n_models, len(axes)):
        axes[idx].axis('off')
    
    fig.colorbar(im, ax=axes.tolist(), fraction=0.02, pad=0.04, label="Transition Probability")
    
    plt.suptitle("Turn-by-Turn Transition Dynamics (Persistence Study)", fontsize=13, fontweight='bold')
    plt.tight_layout()
    
    out_path = os.path.join(figdir, "figure2_transition_matrices.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    print(f"Saved {out_path}")

def main(in_dir, figdir):
    persistence_files = [
        f for f in os.listdir(in_dir)
        if f.startswith("persistence_") and f.endswith(".json") and "_stats" not in f
    ]
    
    if not persistence_files:
        print(f"Warning: No persistence JSON files found in {in_dir}")
        return
    
    all_sequences = {}
    
    for filename in persistence_files:
        json_path = os.path.join(in_dir, filename)
        print(f"Loading sequences from {filename}")
        
        sequences_by_model = load_sequences(json_path)
        
        for model, sequences in sequences_by_model.items():
            if model not in all_sequences:
                all_sequences[model] = {}
            for seq_key, seq_items in sequences.items():
                unique_key = f"{filename}:{seq_key}"
                all_sequences[model][unique_key] = seq_items
    
    if not all_sequences:
        print("Warning: No valid sequences found")
        return
    
    print(f"Found {len(all_sequences)} models:")
    for model, seqs in all_sequences.items():
        # Count multi-turn sequences
        multi_turn = sum(1 for seq in seqs.values() if len(seq) >= 2)
        print(f"  {model}: {len(seqs)} sequences ({multi_turn} with 2+ turns)")
    
    plot_all_transitions(all_sequences, figdir)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", required=True)
    ap.add_argument("--figdir", required=True)
    args = ap.parse_args()
    main(args.in_dir, args.figdir)
