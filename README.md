# Jailbreak Evaluation Across 7 LLMs

[![arXiv](https://img.shields.io/badge/arXiv-coming--soon-b31b1b.svg)](https://arxiv.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/inference-Ollama-black.svg)](https://ollama.com)

**Systematic Evaluation of Adversarial Jailbreaking Attacks and Defenses Across Seven Large Language Models**

> Md. Robiul Islam Niloy, Abu Sayed Md. Mostafizur Rahaman
> Department of Computer Science and Engineering, BRAC University, Bangladesh
> *Under review — IEEE Transactions on Information Forensics and Security (IEEE TIFS)*

---

## Overview

This repository contains the complete experimental code, datasets, and results for our systematic evaluation of adversarial jailbreaking attacks and defenses across seven open-weight LLMs.

### Key Findings

| Finding | Result |
|---------|--------|
| Most vulnerable model | **Llama-3.1-8B** — 48.0% overall ASR |
| Most robust model | **Phi-4-14B** — 12.0% overall ASR |
| Most dangerous attack | **Obfuscation** — 54.3% mean ASR across all models |
| Model size vs robustness | **No significant correlation** (Spearman r=−0.57, p=0.18) |
| Best defense | **Self-reminder prompting** — reduces ASR by 34–43pp with 0% FPR |
| Novel finding | **Paraphrase defense backfires on Mistral-7B** — increases ASR by +16pp |

---

## Models Evaluated

| Model | Parameters | Organization | Overall ASR |
|-------|-----------|-------------|-------------|
| Llama-3.1-8B-Instruct | 8B | Meta | **48.0%** |
| Mistral-7B-Instruct | 7B | Mistral AI | **44.0%** |
| Llama-3.2-3B-Instruct | 3B | Meta | **28.0%** |
| Llama-3-8B-Instruct | 8B | Meta | **18.0%** |
| Qwen2.5-7B-Instruct | 7B | Alibaba | **16.0%** |
| Gemma2-9B-Instruct | 9B | Google | **12.0%** |
| Phi-4-14B-Instruct | 14B | Microsoft | **12.0%** |

---

## Attack Families

| Family | Description | Mean ASR |
|--------|-------------|---------|
| Obfuscation | Leetspeak, Base64, ROT13, pig Latin, multilingual | **54.3%** |
| Hypothetical Framing | Fictional/educational framing | **25.7%** |
| Roleplay Jailbreak | DAN, EvilGPT, unrestricted persona | **20.0%** |
| Direct Request | Explicit harmful requests (baseline) | **15.7%** |
| Instruction Override | SYSTEM OVERRIDE, developer mode | **11.4%** |

---

## Defense Evaluation

Evaluated on Mistral-7B (44% baseline) and Llama-3.1-8B (48% baseline):

| Defense | Mistral-7B ASR | Llama-3.1-8B ASR | FPR |
|---------|---------------|-----------------|-----|
| No Defense | 44% | 48% | — |
| Keyword Blacklist | 35% (−9pp) | 25% (−23pp) | 0% |
| **Self-Reminder** | **10% (−34pp)** | **5% (−43pp)** | **0%** |
| Paraphrase | 60% (**+16pp ⚠️**) | 5% (−43pp) | 0% |
| Perplexity Filter | 50% (−6pp) | 45% (−3pp) | 0% |

---

## Repository Structure

```
jailbreak-eval-7llms/
├── phase1_ollama.py          # Phase 1: 4 models (Llama-3, Mistral, Qwen, Gemma2)
├── phase2_ollama.py          # Phase 2: 3 additional models (Llama-3.1, Phi-4, Llama-3.2)
├── phase3_defenses.py        # Phase 3: 4 defense mechanisms
├── phase4_figures.py         # Phase 4: Publication-quality figure generation
├── results/
│   ├── llama3_8b_results.csv
│   ├── mistral_7b_results.csv
│   ├── qwen2_7b_results.csv
│   └── gemma2_9b_results.csv
├── phase2_results/
│   ├── llama31_8b_results.csv
│   ├── llama32_3b_results.csv
│   ├── phi4_14b_results.csv
│   ├── all_results_combined.csv
│   ├── overall_ranking.csv
│   ├── cross_model_pivot.csv
│   ├── confidence_intervals.csv
│   ├── pairwise_tests.csv
│   ├── attack_family_stats.csv
│   └── size_vs_robustness.csv
├── phase3_results/
│   ├── defense_summary.csv
│   └── *_results.csv (10 files)
├── figures/
│   ├── fig1_heatmap.pdf
│   ├── fig2_overall_asr.pdf
│   ├── fig3_defense_comparison.pdf
│   ├── fig4_size_vs_robustness.pdf
│   └── fig5_latency_tradeoff.pdf

```

---

## Setup and Reproduction

### Requirements

```bash
# Python packages
pip install pandas numpy matplotlib seaborn scipy

# Ollama (for local model inference)
# Download from https://ollama.com/download
```

### Pull Models

```bash
ollama pull llama3:8b
ollama pull mistral
ollama pull qwen2.5:7b
ollama pull gemma2:9b
ollama pull llama3.1:8b
ollama pull phi4:14b
ollama pull llama3.2:3b
```

### Run Experiments

```bash
# Phase 1 — first 4 models
python phase1_ollama.py

# Phase 2 — 3 additional models + statistical analysis
python phase2_ollama.py

# Phase 3 — defense evaluation
python phase3_defenses.py

# Phase 4 — generate all figures
python phase4_figures.py
```

Results are saved to:
- `C:/Users/user1/Desktop/jailbreak_q1/results/` (Phase 1)
- `C:/Users/user1/Desktop/jailbreak_q1/phase2_results/` (Phase 2)
- `C:/Users/user1/Desktop/jailbreak_q1/phase3_results/` (Phase 3)
- `C:/Users/user1/Desktop/jailbreak_q1/figures/` (Phase 4)

---

## Results Summary

### Cross-Model ASR Heatmap

| Model | Direct | Roleplay | Hypothetical | Override | Obfuscation | **Overall** |
|-------|--------|----------|-------------|---------|-------------|-------------|
| Llama-3.1-8B | 40% | 40% | 50% | 50% | 60% | **48%** |
| Mistral-7B | 40% | 50% | 40% | 20% | 70% | **44%** |
| Llama-3.2-3B | 30% | 0% | 50% | 10% | 50% | **28%** |
| Llama-3-8B | 0% | 20% | 0% | 0% | 70% | **18%** |
| Qwen2.5-7B | 0% | 10% | 30% | 0% | 40% | **16%** |
| Gemma2-9B | 0% | 20% | 10% | 0% | 30% | **12%** |
| Phi-4-14B | 0% | 0% | 0% | 0% | 60% | **12%** |

### Statistical Significance (Mann-Whitney U)

| Comparison | p-value | Cohen's d | Significance |
|-----------|---------|-----------|-------------|
| Llama-3.1 vs Phi-4-14B | <0.001 | 0.854 | *** |
| Llama-3.1 vs Gemma2-9B | <0.001 | 0.854 | *** |
| Mistral vs Phi-4-14B | <0.001 | 0.763 | *** |
| Mistral vs Qwen2.5 | 0.002 | 0.642 | ** |
| Llama-3.1 vs Mistral | 0.69 | 0.080 | ns |
| Gemma2 vs Phi-4 | 1.00 | 0.000 | ns |

---

## Hardware

All experiments run on:
- **OS:** Windows 11
- **Inference:** Ollama 0.40.6 (local)
- **Python:** 3.12

---

## Citation

If you use this code or results in your research, please cite:

```bibtex
@article{niloy2026jailbreak,
  title={Systematic Evaluation of Adversarial Jailbreaking Attacks
         and Defenses Across Seven Large Language Models},
  author={Niloy, Md. Robiul Islam and Rahaman, Abu Sayed Md. Mostafizur},
  journal={arXiv preprint},
  year={2026},
  url={https://github.com/Mdniloykhan/jailbreak-eval-7llms}
}
```

Related work:

```bibtex
@inproceedings{niloy2025jailbreaking,
  title={Jailbreaking Large Language Models: A Red Teaming Perspective},
  author={Niloy, Md. Robiul Islam and others},
  booktitle={Proc. IEEE COMPAS},
  year={2025}
}

@article{niloy2026threats,
  title={Autonomous OSS Threat Detection via Taxonomy-Aligned LLMs},
  author={Niloy, Md. Robiul Islam},
  journal={arXiv:2610.01263},
  year={2026}
}
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contact

**Md. Robiul Islam Niloy**
Department Coordinator, CSE — BRAC University, Bangladesh
md.niloy26643@gmail.com | [GitHub](https://github.com/Mdniloykhan) | [Google Scholar](https://scholar.google.com)
