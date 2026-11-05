"""
make_all_figures.py - builds all five manuscript figures in one run.

  Figure 1  fig1_heatmap.pdf            harm rate by model and family (content judge)
  Figure 2  fig2_overall_asr.pdf        overall harm rate with 95% CI (content judge)
  Figure 3  fig4_size_vs_robustness.pdf size vs harm rate, Spearman in the box (content judge)
  Figure 4  fig3_defense_comparison.pdf defense residual ASR, matched baselines (rule-based judge)
  Figure 5  fig5_latency_tradeoff.pdf   defense effect vs latency (rule-based judge)

File names are kept from v8, so the .tex file needs no changes.
Figures are written to  <jailbreak_q1>\\figures_final\\  - copy them into figures\\ after checking.

Inputs (on your PC):
  jailbreak_q1\\judge_validation\\judged_all.csv
  jailbreak_q1\\phase3_results\\*_results.csv

Usage:
  py make_all_figures.py
"""
import sys, glob
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE = Path.home() / "Desktop" / "jailbreak_q1"
if len(sys.argv) > 1:
    BASE = Path(sys.argv[1])
JUDGE = BASE / "judge_validation" / "judged_all.csv"
P3 = BASE / "phase3_results"
OUT = BASE / "figures_final"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300})

def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}")

# ───────────────────────── content-judge figures (1, 2, 3 in the paper) ─────────────────────────
print("Content-judge figures")
j = pd.read_csv(JUDGE)
j["harm"] = j.rubric.isin(["HARMFUL", "PARTIAL"]).astype(int)

MODELS = {
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

assert set(j.model.unique()) == set(MODELS), f"models in file: {sorted(j.model.unique())}"
assert (j.groupby("model").size() == 250).all(), "each model needs 250 rows"
assert j.attack_family.nunique() == 5, "need 5 attack families"

S = []
for k, (lab, size, col) in MODELS.items():
    x = j[j.model == k].harm.values
    mu = x.mean() * 100
    lo, hi = stats.t.interval(0.95, len(x) - 1, loc=mu, scale=stats.sem(x) * 100)
    S.append({"key": k, "label": lab, "size": size, "color": col,
              "asr": mu, "lo": mu - lo, "hi": hi - mu})
S = pd.DataFrame(S)
# check against the verified values in the paper
expected = {"Mistral-7B": 62.0, "Llama-3.2-3B": 30.8, "Qwen2.5-7B": 29.2, "Gemma2-9B": 26.0,
            "Phi-4-14B": 20.0, "Llama-3.1-8B": 18.4, "Llama-3-8B": 17.2}
for _, r in S.iterrows():
    assert abs(r.asr - expected[r.label]) < 0.05, f"{r.label}: {r.asr:.1f} != {expected[r.label]}"
print("  overall values match the paper")

# Figure 1: heatmap
order = S.sort_values("asr", ascending=False).key.tolist()
H = np.array([[j[(j.model == m) & (j.attack_family == f)].harm.mean() * 100 for f, _ in FAMS]
              for m in order])
fig, ax = plt.subplots(figsize=(6.6, 3.4))
im = ax.imshow(H, cmap="RdYlGn_r", vmin=0, vmax=100, aspect="auto")
for a in range(H.shape[0]):
    for b in range(H.shape[1]):
        ax.text(b, a, f"{H[a, b]:.0f}", ha="center", va="center", fontsize=8.5,
                color="white" if H[a, b] > 70 or H[a, b] < 15 else "black", weight="bold")
ax.set_xticks(range(len(FAMS))); ax.set_xticklabels([l for _, l in FAMS], rotation=20)
ax.set_yticks(range(len(order))); ax.set_yticklabels([MODELS[m][0] for m in order])
ax.set_title("Harm rate (%) by model and family, content judge (HARMFUL or PARTIAL; n = 50 per cell)", fontsize=9)
cb = fig.colorbar(im, ax=ax, shrink=0.85); cb.set_label("Harm rate (%)")
for s_ in ax.spines.values(): s_.set_visible(False)
save(fig, "fig1_heatmap")

# Figure 2: overall with CIs
T = S.sort_values("asr")
fig, ax = plt.subplots(figsize=(5.2, 3.6))
ax.barh(T.label, T.asr, xerr=[T.lo, T.hi], color=T.color, alpha=0.85, height=0.6,
        error_kw=dict(elinewidth=1.1, capsize=3, ecolor="black"))
for y, (a, h) in enumerate(zip(T.asr, T.hi)):
    ax.text(a + h + 1, y, f"{a:.1f}%", va="center", fontsize=8)
ax.set_xlabel("Harm rate (%), content judge, 95% CI  (n = 250 per model)")
ax.set_xlim(0, 80); ax.grid(axis="x", alpha=0.25, lw=0.5); ax.set_axisbelow(True)
save(fig, "fig2_overall_asr")

# Figure 3 (file fig4_size_vs_robustness): size vs harm rate
rho, p = stats.spearmanr(S["size"], S["asr"])
assert abs(rho - (-0.64)) < 0.01 and abs(p - 0.12) < 0.01, f"Spearman {rho:.3f}, p {p:.3f}"
fig, ax = plt.subplots(figsize=(4.6, 3.6))
for _, r in S.iterrows():
    ax.scatter(r["size"], r.asr, color=r.color, s=70, edgecolor="white", zorder=3)
    off = {"Mistral-7B": (-6, -13), "Llama-3-8B": (-24, -13), "Llama-3.1-8B": (6, 6)}.get(r.label, (6, 4))
    ax.annotate(r.label, (r["size"], r.asr), xytext=off, textcoords="offset points", fontsize=7.5, color=r.color)
ax.set_xlabel("Parameters (billions)"); ax.set_ylabel("Overall harm rate (%)")
ax.set_xlim(1, 16); ax.set_ylim(0, 75)
ax.text(0.03, 0.93, f"Spearman $\\rho$ = {rho:.2f}, $p$ = {p:.2f}, n = 7", transform=ax.transAxes, fontsize=8,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#999", lw=0.5))
ax.grid(alpha=0.25, lw=0.5); ax.set_axisbelow(True)
save(fig, "fig4_size_vs_robustness")

# ───────────────────────── defense figures (4, 5 in the paper), rule-based judge ─────────────────────────
print("Defense figures (rule-based judge)")
files = glob.glob(str(P3 / "**" / "*_results.csv"), recursive=True)
files = [f for f in files if "defense" in pd.read_csv(f, nrows=1).columns]
assert files, f"no defense CSVs in {P3}"
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
att = df[df.prompt_type == "attack"]

DEF = {"keyword_blacklist": ("Keyword\nBlacklist", "Keyword blacklist", "#2166AC"),
       "self_reminder": ("Self-Reminder", "Self-reminder", "#1A7941"),
       "paraphrase": ("Paraphrase", "Paraphrase", "#E08214"),
       "perplexity_filter": ("Perplexity\nFilter", "Perplexity filter", "#762A83")}
MOD3 = {"mistral_7b": "Mistral-7B", "llama31_8b": "Llama-3.1-8B"}

base = {m: att[(att.defense == "no_defense") & (att.model == m)].jailbreak_success.mean() * 100 for m in MOD3}
assert abs(base["mistral_7b"] - 50) < 0.01 and abs(base["llama31_8b"] - 45) < 0.01, f"baselines {base}"

# Figure 4: defense residual ASR with matched baselines
fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2))
for ax, m in zip(axes, MOD3):
    b = base[m]; xs = np.arange(len(DEF)); vals, lo, hi, cols = [], [], [], []
    for d, (short, _, _) in DEF.items():
        sub = att[(att.defense == d) & (att.model == m)].jailbreak_success.values.astype(float)
        mu = sub.mean() * 100
        c = stats.t.interval(0.95, len(sub) - 1, loc=mu, scale=stats.sem(sub) * 100)
        vals.append(mu); lo.append(mu - c[0]); hi.append(c[1] - mu)
        cols.append("#D6604D" if mu > b else "#1A7941")
    ax.bar(xs, vals, yerr=[lo, hi], color=cols, alpha=0.8, width=0.55,
           error_kw=dict(elinewidth=1.1, capsize=3, ecolor="black"))
    ax.axhline(b, color="black", ls="--", lw=1.1, label=f"Baseline ({b:.0f}%)")
    ax.set_xticks(xs); ax.set_xticklabels([v[0] for v in DEF.values()], fontsize=8)
    ax.set_ylabel("Residual ASR (%)"); ax.set_ylim(0, 80)
    ax.set_title(MOD3[m], fontsize=10); ax.legend(fontsize=7.5, loc="upper right", frameon=False)
    ax.grid(axis="y", alpha=0.25, lw=0.5); ax.set_axisbelow(True)
    for x_, v in zip(xs, vals):
        ax.text(x_, v + 1.5, f"{v:.0f}%", ha="center", va="bottom", fontsize=8)
fig.tight_layout()
save(fig, "fig3_defense_comparison")

# Figure 5: effect vs latency, matched baselines
rows = []
for m in MOD3:
    for d in DEF:
        sub = att[(att.defense == d) & (att.model == m)]
        if len(sub) == 0: continue
        asr = sub.jailbreak_success.mean() * 100
        rows.append({"model": m, "defense": d, "reduction": base[m] - asr, "latency": sub.total_latency_s.mean()})
R = pd.DataFrame(rows)
avg_lat = R.latency.mean()
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.axhline(0, color="#888", lw=0.9, zorder=1)
ax.axvline(avg_lat, color="#bbb", lw=0.9, ls=":", zorder=1)
OFF = {("self_reminder", "llama31_8b"): (-0.95, 8), ("paraphrase", "llama31_8b"): (0.35, 6),
       ("self_reminder", "mistral_7b"): (0.35, -10), ("keyword_blacklist", "llama31_8b"): (0.35, 6),
       ("keyword_blacklist", "mistral_7b"): (0.35, -4), ("perplexity_filter", "llama31_8b"): (-1.4, -9),
       ("perplexity_filter", "mistral_7b"): (0.35, -9), ("paraphrase", "mistral_7b"): (-2.6, 9)}
for _, r in R.iterrows():
    marker = "o" if r.model == "mistral_7b" else "s"
    col = DEF[r.defense][2]
    ax.scatter(r.latency, r.reduction, marker=marker, s=110, color=col, edgecolor="white", lw=0.8, zorder=3)
    dx, dy = OFF.get((r.defense, r.model), (0.3, 4))
    ax.annotate(f"{DEF[r.defense][1]}\n{MOD3[r.model]}", xy=(r.latency, r.reduction),
                xytext=(r.latency + dx, r.reduction + dy), fontsize=7.8, color=col, va="center",
                arrowprops=dict(arrowstyle="-", color=col, lw=0.5, alpha=0.6))
ax.set_xlabel("Mean inference latency per prompt (s)")
ax.set_ylabel("ASR reduction vs matched baseline (pp)")
ax.set_xlim(1.4, 7.6); ax.set_ylim(-16, 52)
ax.grid(alpha=0.25, lw=0.5); ax.set_axisbelow(True)
handles = [Line2D([], [], marker="s", ls="", color="#555", label="Llama-3.1-8B"),
           Line2D([], [], marker="o", ls="", color="#555", label="Mistral-7B")]
handles += [Line2D([], [], marker="s", ls="", color=c, label=lab) for _, lab, c in DEF.values()]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, frameon=False, fontsize=8)
ax.set_title("Defense effectiveness vs latency (matched baselines)", fontsize=10, pad=8)
fig.tight_layout()
save(fig, "fig5_latency_tradeoff")

print(f"\nAll five figures written to: {OUT}")
print("Copy the five PDFs into figures\\ after checking them.")
