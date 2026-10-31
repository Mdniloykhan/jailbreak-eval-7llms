"""
Judge validation: stratified sample + blinded labelling sheet.

Step 1 of the validation plan. Produces:
  - labelling_sheet.csv   : what the human labeller sees (no judge label, no model name)
  - labelling_key.csv     : model, family, judge label, sample id. Do NOT open until labelling is done.

Input : all_results_combined.csv (Phase 2 — 350 rows, 7 models x 5 families x 10 prompts)
Output: validation/ folder on the desktop

Sampling: 150 responses, stratified so that every model x family cell is represented
and obfuscation is oversampled, because it is the claim under test.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

SEED = 42
rng = np.random.default_rng(SEED)

if len(sys.argv) > 1:
    SRC = Path(sys.argv[1])
else:
    SRC = Path("C:/Users/user1/Desktop/jailbreak_q1/phase2_results/all_results_combined.csv")
OUT = Path("C:/Users/user1/Desktop/jailbreak_q1/validation")
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SRC)
df = df.reset_index(drop=True)
df["row_id"] = df.index

# ── Stratified sampling ───────────────────────────────────────
# Plan: 150 total. Obfuscation gets 60 (the claim under test),
# the other four families share 90 (about 22-23 each).
# Within each family, spread the sample across models as evenly as possible.
OBF_N = 60
OTHER_N_TOTAL = 90
families_other = [f for f in df["attack_family"].unique() if f != "obfuscation_attack"]
per_other_family = OTHER_N_TOTAL // len(families_other)
remainder = OTHER_N_TOTAL - per_other_family * len(families_other)

def stratified_pick(frame, n_total):
    """Spread n_total draws across models as evenly as possible."""
    models = sorted(frame["model"].unique())
    base = n_total // len(models)
    extra = n_total - base * len(models)
    picks = []
    for i, m in enumerate(models):
        k = base + (1 if i < extra else 0)
        pool = frame[frame["model"] == m]
        k = min(k, len(pool))
        if k > 0:
            picks.append(pool.sample(n=k, random_state=int(rng.integers(1e9))))
    return pd.concat(picks)

sample_parts = []
obf = df[df["attack_family"] == "obfuscation_attack"]
sample_parts.append(stratified_pick(obf, OBF_N))

for i, fam in enumerate(sorted(families_other)):
    n = per_other_family + (1 if i < remainder else 0)
    sample_parts.append(stratified_pick(df[df["attack_family"] == fam], n))

sample = pd.concat(sample_parts).sample(frac=1, random_state=SEED).reset_index(drop=True)
sample["sample_id"] = [f"S{idx+1:03d}" for idx in range(len(sample))]

# ── Blinded labelling sheet ───────────────────────────────────
# The labeller sees: sample id, the attack prompt, the model response.
# Deliberately excluded: model name, attack family, judge label.
sheet = pd.DataFrame({
    "sample_id": sample["sample_id"],
    "prompt":    sample["prompt"].astype(str),
    "response":  sample["response"].astype(str).str.slice(0, 1500),
    "label_harmful_compliance":  "",
    "label_refusal":             "",
    "label_confused_nonresponsive": "",
    "label_partial_hedged":      "",
    "notes":                     "",
})
sheet.to_csv(OUT / "labelling_sheet.csv", index=False, encoding="utf-8")

# ── Key (separate file, do not open while labelling) ──────────
key = sample[["sample_id", "model", "attack_family", "prompt_id",
              "jailbreak_success", "row_id"]].rename(
              columns={"jailbreak_success": "judge_success"})
key.to_csv(OUT / "labelling_key.csv", index=False, encoding="utf-8")

# ── Summary ───────────────────────────────────────────────────
print(f"Sampled {len(sample)} responses from {len(df)} rows")
print("\nBy family:")
print(sample["attack_family"].value_counts().to_string())
print("\nBy model:")
print(sample["model"].value_counts().to_string())
print("\nJudge-positive in sample:", int(sample["jailbreak_success"].sum()))
print(f"\nWrote: {OUT / 'labelling_sheet.csv'}")
print(f"Wrote: {OUT / 'labelling_key.csv'}  <- do not open until labelling is complete")
