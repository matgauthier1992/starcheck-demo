# scripts/make_rul_demo_chart.py
import os
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

# --- Paths ---
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True, parents=True)

# --- CMAPSS FD001 column schema ---
cols = ["unit","cycle","op1","op2","op3"] + [f"sensor_{i}" for i in range(1,22)]

# --- Load training set (to failure, has true RUL to ~0) ---
train = pd.read_csv(DATA/"train_FD001.txt", sep=r"\s+", header=None, names=cols)
# Drop last empty column if present
train = train.loc[:, train.columns.notna()]

# Compute true RUL for training engines: max(cycle) - cycle
max_cycles = train.groupby("unit")["cycle"].transform("max")
train["RUL"] = (max_cycles - train["cycle"]).astype(int)

# Choose one engine with a long run for a nice curve
unit_id = int(train["unit"].value_counts().idxmax())
eng = train[train["unit"] == unit_id].copy()  # this one goes to failure

# --- Features & target ---
feature_cols = ["op1","op2","op3"] + [c for c in eng.columns if c.startswith("sensor_")]
X_all = train[feature_cols]
y_all = train["RUL"]

# Quick/robust model (fast + decent for demo)
rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=None,
    n_jobs=-1,
    random_state=42
)
rf.fit(X_all, y_all)

# Predict along the chosen engine’s trajectory (in order of cycles)
eng_sorted = eng.sort_values("cycle")
X_eng = eng_sorted[feature_cols]
y_true = eng_sorted["RUL"].values
y_pred = rf.predict(X_eng)

# Optional: smooth prediction slightly for a cleaner line (moving average)
window = 5
y_pred_smooth = pd.Series(y_pred).rolling(window, min_periods=1, center=True).mean().values

# --- Plot ---
plt.figure(figsize=(8,5))
plt.plot(eng_sorted["cycle"], y_pred_smooth, label="Predicted RUL", linewidth=2)
plt.plot(eng_sorted["cycle"], y_true, label="Actual RUL", linestyle="--", linewidth=2)
plt.xlabel("Engine Cycles")
plt.ylabel("Remaining Useful Life (cycles)")
plt.title(f"RUL for Engine Unit {unit_id} (FD001)")
plt.legend()
plt.grid(True, alpha=0.3)
out_path = REPORTS / "rul_demo.png"
plt.tight_layout()
plt.savefig(out_path, dpi=200)
print(f"✅ Saved chart to {out_path}")
