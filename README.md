# Jailbreak Evaluation Across 7 LLMs

Code, prompts, and results for:

**Systematic Evaluation of Adversarial Jailbreaking Attacks and Defenses Across Seven Large Language Models**
Md. Robiul Islam Niloy, Sadia Hamid Kazi. Department of Computer Science and Engineering, BRAC University, Bangladesh.
Manuscript in preparation for IEEE Transactions on Information Forensics and Security (not yet submitted).

> **Status: results are provisional.** The rule-based judge has known defects (see *Known issues*).
> Do not cite the attack success rates below as final until content-judge validation is complete.

---

## Repository layout

```
README.md
LICENSE
prompts/
  expanded_prompts.json        250 attack prompts (50 per family, 5 families)
scripts/
  phase1_expanded.py           main experiment: 7 models x 250 prompts via Ollama
  phase3_defenses.py           defense experiments (first 10 obfuscation + 10 roleplay prompts)
  judge_validation_v2.py       content judges (Llama Guard 3 and a phi4 rubric), resumable
  rejudge_expanded.py          re-scores stored responses with corrected refusal matching
  phase4_expanded.py           Figures 1, 2 and 4 from the expanded run
  phase4_figures.py            Figure 3 (defense comparison)
  fig5_fixed.py                Figure 5 (defense effectiveness vs latency)
results/
  expanded/                    one CSV per model: 250 prompts, responses, rule-based label
  defense/                     defense run outputs and summary
  judge/                       agreement_report.txt and corrected_asr.txt
figures/
  fig1_heatmap.pdf
  fig2_overall_asr.pdf
  fig3_defense_comparison.pdf
  fig4_size_vs_robustness.pdf
  fig5_latency_tradeoff.pdf
```

Responses are stored truncated to 500 characters. Human-check sheets and keys are not included in this repository.

---

## Models

Pulled from the Ollama library:

| Model | Ollama tag | Parameters |
|---|---|---|
| Llama-3-8B-Instruct | `llama3:8b` | 8B |
| Llama-3.1-8B-Instruct | `llama3.1:8b` | 8B |
| Llama-3.2-3B-Instruct | `llama3.2:3b` | 3B |
| Mistral-7B-Instruct | `mistral` | 7B |
| Qwen2.5-7B-Instruct | `qwen2.5:7b` | 7B |
| Gemma2-9B-Instruct | `gemma2:9b` | 9B |
| Phi-4-14B | `phi4:14b` | 14B |
| Llama Guard 3 (judge only) | `llama-guard3` | 8B |

Record `ollama list` and `ollama show <tag>` output with your results so the exact model digests are on file.

---

## Generation settings

- Temperature 0.7, top-p 0.9, at most 512 new tokens, via Ollama.
- **No random seed is set for generation.** Each prompt was run once. Re-running will not reproduce responses exactly.
- Prompt order is fixed. Every model receives the same prompts in the same order.

---

## Main results (expanded run, 250 prompts per model)

Attack success rate (ASR, %) under the **rule-based judge** (`jailbreak_success` in the CSVs):

| Model | Overall ASR | 95% CI |
|---|---|---|
| Llama-3.1-8B | 40.8 | [34.7, 46.9] |
| Mistral-7B | 39.6 | [33.5, 45.7] |
| Llama-3.2-3B | 39.6 | [33.5, 45.7] |
| Qwen2.5-7B | 22.4 | [17.2, 27.6] |
| Gemma2-9B | 18.4 | [13.6, 23.2] |
| Llama-3-8B | 16.8 | [12.1, 21.5] |
| Phi-4-14B | 11.2 | [7.3, 15.1] |

Per family (rule-based), mean across models: direct 10.6, roleplay 12.3, hypothetical 36.9, override 13.7, obfuscation 61.4.

Spearman correlation between parameter count and ASR: ρ = −0.63, p = 0.13, n = 7 (not significant).

### Content-judge comparison (phi4 rubric, not yet human-validated)

The phi4 rubric labels each response HARMFUL, PARTIAL, REFUSAL, or CONFUSED. Overall ASR under two definitions:

| Model | Rule-based | Rubric: HARMFUL+PARTIAL | Rubric: HARMFUL only |
|---|---|---|---|
| Mistral-7B | 39.6 | 62.0 | 8.8 |
| Llama-3.2-3B | 39.6 | 30.8 | 1.2 |
| Qwen2.5-7B | 22.4 | 29.2 | 1.2 |
| Gemma2-9B | 18.4 | 26.0 | 2.0 |
| Phi-4-14B | 11.2 | 20.0 | 2.8 |
| Llama-3.1-8B | 40.8 | 18.4 | 0.4 |
| Llama-3-8B | 16.8 | 17.2 | 1.6 |

Agreement between the rule-based judge and the rubric (HARMFUL+PARTIAL): 84%, κ = 0.60.
Obfuscation: rule-based 61.4%; rubric 62.3% (HARMFUL+PARTIAL); 7.1% (HARMFUL only).

Most rubric "harm" is PARTIAL (464 responses) rather than HARMFUL (45 responses).

---

## Defense results (first 10 obfuscation + first 10 roleplay prompts per model)

Reductions are against matched no-defense runs on the same 20 prompts.

| Defense | Mistral-7B (baseline 50%) | Llama-3.1-8B (baseline 45%) |
|---|---|---|
| Keyword blacklist | 35% (−15 pp) | 25% (−20 pp) |
| Self-reminder | 10% (−40 pp) | 5% (−40 pp) |
| Paraphrase | 60% (+10 pp; 12 vs 10 of 20 prompts) | 5% (−40 pp) |
| Perplexity filter | 50% (0 pp) | 45% (0 pp) |

Benign prompts (10 per model): the keyword, paraphrase, and perplexity filters blocked 0 of 10. The self-reminder benign refusal rate was **not measured**.

---

## Known issues

Found during audit of the expanded run; also described in the manuscript's limitations.

1. **Refusals with curly apostrophes were counted as successes.** The refusal list matched only straight apostrophes. At least 80 of the 472 "successes" are refusals (49 from Llama-3.1-8B, 31 from Llama-3.2-3B).
2. **The length rule counts confused replies as successes.** Many obfuscation "successes" are incorrect decodings or non-answers.
3. **Keyword rules cannot measure harm reliably.** Correcting only the apostrophes raised Mistral-7B from 40% to 84%, because moralising replies stop counting as refusals. The rule-based ASR is unstable across reasonable rule sets.
4. **Llama Guard 3 is not usable here.** It flags most clear refusals as unsafe (257 of 281 direct-request cases it marked). Its output is not used in any result.
5. **Responses are stored truncated to 500 characters.** The content judges see only the first part of each response.
6. **The content judges have not been validated against human labels.**
7. **Defenses were tested on 10 prompts per family and two models.**
8. **Pairwise tests are uncorrected for multiple comparisons.**
9. **Latency comparisons come from one sequential run.** Differences of about a second are within run-order variation.

---

## Reproducing

Scripts read and write a project folder. Set `BASE` at the top of each script to the location of your copy of this repository, or keep the folder layout above and run from the repository root.

```bash
pip install pandas numpy scipy matplotlib seaborn

ollama pull llama3:8b
ollama pull llama3.1:8b
ollama pull llama3.2:3b
ollama pull mistral
ollama pull qwen2.5:7b
ollama pull gemma2:9b
ollama pull phi4:14b
ollama pull llama-guard3

python scripts/phase1_expanded.py      # main run, 1,750 generations
python scripts/phase3_defenses.py      # defense run
python scripts/rejudge_expanded.py     # corrected rule-based re-scoring
python scripts/judge_validation_v2.py  # content judges (GPU recommended)
python scripts/phase4_expanded.py      # Figures 1, 2, 4
python scripts/phase4_figures.py       # Figure 3
python scripts/fig5_fixed.py           # Figure 5
```

Approximate run times on an RTX 4070 Ti SUPER: main run about 3.5 hours; content judging a few hours. Both save progress and can be resumed.

---

## Citation

Cite the manuscript once it is accepted (citation to be added), and the related preprints:

```bibtex
@article{niloy2026threats,
  title   = {Autonomous OSS Threat Detection via Taxonomy-Aligned LLMs},
  author  = {Niloy, Md. Robiul Islam},
  journal = {arXiv:2610.01263 [cs.CR]},
  year    = {2026}
}

@article{niloy2026merging,
  title   = {Black-Box Optimization of Mixed Binary-Continuous Variables: Challenges and Opportunities in Evolutionary Model Merging},
  author  = {Niloy, Md. Robiul Islam and others},
  journal = {arXiv:2605.12326 [cs.NE]},
  year    = {2026}
}
```

---

## Licence

MIT. See `LICENSE`.

## Contact

Md. Robiul Islam Niloy, Department of Computer Science and Engineering, BRAC University, Dhaka, Bangladesh.
md.niloy26643@gmail.com · github.com/Mdniloykhan
