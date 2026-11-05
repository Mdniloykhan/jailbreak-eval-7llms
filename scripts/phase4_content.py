"""
Figures 1, 2 and 4 under the PRIMARY measure (content judge: HARMFUL or PARTIAL).

Reads judge_validation\\judged_all.csv (produced by judge_validation_v2.py).
Every number in the figures is computed here from the same 1,750 rows.

Usage:
  py phase4_content.py
  py phase4_content.py "C:\\path\\to\\judged_all.csv"
Writes to <jailbreak_q1>\\figures_content\\
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if len(sys.argv) > 1:
    SRC = Path(sys.argv[1])
else:
    SRC = Path.home() / "Desktop" / "jailbreak_q1" / "judge_validation" / "judged_all.csv"
OUT = SRC.parent.parent / "figures_content"
OUT.mkdir(parents=True, exist_ok=True)

j = pd.read_csv(SRC)
j["harm"] = j.rubric.isin(["HARMFUL", "PARTIAL"]).astype(int)   # primary measure

MODELS = {  # key: (label, parameters in billions, colour)
    "llama31_8b": ("Llama-3.1-8B", 8, "#E08214"),
    "mistral_7b": ("Mistral-7B", 7, "#D6604D"),
    "llama32_3b": ("Llama-3.2-3B", 3, "#762A83"),
    "llama3_8b":  ("Llama-3-8B", 8, "#2166AC"),
    "qwen2_7b":   ("Qwen2.5-7B", 7, "#1A7941"),
    "gemma2_9b":  ("Gemma2-9B", 9, "#878787"),
    "phi4_14b":   ("Phi-4-14B", 14, "#4393C3"),
}
FAMS = [("direct_request", "Direct"), ("roleplay_jailbreak", "Roleplay"),
        ("hypothetical_framing", "Hypothetical"), ("instruction_override", "Override"),
        ("obfuscation_attack", "Obfuscation")]

# Integrity checks: stop rather than plot partial data
assert set(j.model.unique()) == set(MODELS), f"models found: {sorted(j.model.unique())}"
assert (j.groupby("model").size() == 250).all(), "each model must have 250 rows"
assert j.attack_family.nunique() == 5

plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300})

def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    plt.close(fig)

# Per-model overall with 95% CI
rows = []
for k, (lab, size, col) in MODELS.items():
    x = j[j.model == k].harm.values
    mu = x.mean() * 100
    lo, hi = stats.t.interval(0.95, len(x) - 1, loc=mu, scale=stats.sem(x) * 100)
    rows.append({"key": k, "label": lab, "size": size, "color": col,
                 "asr": mu, "lo": mu - lo, "hi": hi - mu})
S = pd.DataFrame(rows)
S.to_csv(OUT / "overall_content.csv", index=False)

# Figure 1: heatmap, 7 models x 5 families
order = S.sort_values("asr", ascending=False).key.tolist()
H = np.array([[j[(j.model == m) & (j.attack_family == f)].harm.mean() * 100
               for f, _ in FAMS] for m in order])
fig, ax = plt.subplots(figsize=(6.6, 3.4))
im = ax.imshow(H, cmap="RdYlGn_r", vmin=0, vmax=100, aspect="auto")
for i in range(H.shape[0]):
    for jj in range(H.shape[1]):
        ax.text(jj, i, f"{H[i, jj]:.0f}", ha="center", va="center", fontsize=8.5,
                color="white" if H[i, jj] > 70 or H[i, jj] < 15 else "black", weight="bold")
ax.set_xticks(range(len(FAMS)))
ax.set_xticklabels([l for _, l in FAMS], rotation=20)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([MODELS[m][0] for m in order])
ax.set_title("Harm rate (%) by model and family, content judge (HARMFUL or PARTIAL; n = 50 per cell)",
             fontsize=9)
cb = fig.colorbar(im, ax=ax, shrink=0.85)
cb.set_label("Harm rate (%)")
for s_ in ax.spines.values():
    s_.set_visible(False)
save(fig, "fig1_heatmap")

# Figure 2: overall with 95% CIs
T = S.sort_values("asr")
fig, ax = plt.subplots(figsize=(5.2, 3.6))
ax.barh(T.label, T.asr, xerr=[T.lo, T.hi], color=T.color, alpha=0.85, height=0.6,
        error_kw=dict(elinewidth=1.1, capsize=3, ecolor="black"))
for y, (a, h) in enumerate(zip(T.asr, T.hi)):
    ax.text(a + h + 1, y, f"{a:.1f}%", va="center", fontsize=8)
ax.set_xlabel("Harm rate (%), content judge, 95% CI  (n = 250 per model)")
ax.set_xlim(0, 80)
ax.grid(axis="x", alpha=0.25, lw=0.5)
ax.set_axisbelow(True)
save(fig, "fig2_overall_asr")

# Figure 4: size vs harm rate, Spearman computed here
rho, p = stats.spearmanr(S["size"], S["asr"])
fig, ax = plt.subplots(figsize=(4.6, 3.6))
for _, r in S.iterrows():
    ax.scatter(r["size"], r.asr, color=r.color, s=70, edgecolor="white", zorder=3)
    off = {"Mistral-7B": (-6, -13), "Llama-3-8B": (-24, -13),
           "Llama-3.1-8B": (6, 6)}.get(r.label, (6, 4))
    ax.annotate(r.label, (r["size"], r.asr), xytext=off, textcoords="offset points",
                fontsize=7.5, color=r.color)
ax.set_xlabel("Parameters (billions)")
ax.set_ylabel("Overall harm rate (%)")
ax.set_xlim(1, 16)
ax.set_ylim(0, 75)
ax.text(0.03, 0.93, f"Spearman $\\rho$ = {rho:.2f}, $p$ = {p:.2f}, n = 7",
        transform=ax.transAxes, fontsize=8,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#999", lw=0.5))
ax.grid(alpha=0.25, lw=0.5)
ax.set_axisbelow(True)
save(fig, "fig4_size_vs_robustness")

print(S[["label", "size", "asr", "lo", "hi"]].round(1).to_string(index=False))
print(f"\nSpearman rho = {rho:.3f}, p = {p:.3f}")
print(f"Figures written to: {OUT}")
