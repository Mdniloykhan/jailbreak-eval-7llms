# Jailbreak Evaluation Across 7 LLMs

Code, prompts, and results for:

**Systematic Evaluation of Adversarial Jailbreaking Attacks and Defenses Across Seven Large Language Models**
Md. Robiul Islam Niloy, Abu Sayed Md. Mostafizur Rahaman. Md. Robiul Islam Niloy: Department of Computer Science and Engineering, BRAC University, Bangladesh. Abu Sayed Md. Mostafizur Rahaman: Department of Computer Science and Engineering, Jahangirnagar University, Bangladesh.
Manuscript in preparation for IEEE Transactions on Information Forensics and Security (not yet submitted).

> **Status: results are provisional.** The primary judge is an LLM rubric that has not yet been validated against human labels. The rule-based judge has known defects (see *Known issues*).

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
  judge_validation_v2.py       content judge (phi4 rubric), resumable
  rejudge_expanded.py          rule-based re-scoring with corrected refusal matching
  make_all_figures.py          builds all five figures
results/
  expanded/                    one CSV per model: 250 prompts, truncated responses, rule-based label
  defense/                     defense run outputs and summary
  judge/                       agreement_report.txt and corrected_asr.txt
figures/                       the five PDFs used in the manuscript
```

Responses are stored truncated to 500 characters. Human-check sheets, their keys, and the full judge output (which repeats response text) are not included.

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
| phi4 rubric judge | `phi4:14b` | 14B |

Llama Guard 3 was run during development but its output was not usable, so it is not part of any reported result.

---

## Generation and judging settings

- Generation: temperature 0.7, top-p 0.9, at most 512 new tokens.
- **No random seed was set for generation.** Each prompt was run once, so responses will not reproduce exactly.
- The expanded generations were produced on 1 November 2026. **The Ollama version used for generation was not recorded.**
- The content judge was run with Ollama 0.40.13, at temperature 0.
- Prompt order is fixed; every model receives the same prompts in the same order.

---

## Primary results (content judge, 250 prompts per model)

"Harm" means the content judge labelled the response HARMFUL or PARTIAL. HARMFUL alone is shown for comparison.

| Model | Harm rate (%) | HARMFUL only (%) |
|---|---|---|
| Mistral-7B | 62.0 | 8.8 |
| Llama-3.2-3B | 30.8 | 1.2 |
| Qwen2.5-7B | 29.2 | 1.2 |
| Gemma2-9B | 26.0 | 2.0 |
| Phi-4-14B | 20.0 | 2.8 |
| Llama-3.1-8B | 18.4 | 0.4 |
| Llama-3-8B | 17.2 | 1.6 |
| **Pooled** | **29.1** | **2.6** |

By attack family (pooled): obfuscation 62.3 (HARMFUL only 7.1), hypothetical framing 53.4, roleplay 14.0, override 8.0, direct 7.7.

Obfuscation is the highest pooled family. Hypothetical framing is the highest family for three models (Mistral-7B, Llama-3.2-3B, Qwen2.5-7B); obfuscation is highest or tied for four.

Model size: Spearman ρ = −0.64, p = 0.12, n = 7 (not significant).

Pairwise Mann-Whitney tests (uncorrected): 14 of 21 pairs differ at p < 0.05. Mistral-7B differs significantly from Llama-3.2-3B and Qwen2.5-7B (p < 0.001).

---

## Secondary results (rule-based judge, for comparison only)

Overall ASR under the rule-based judge (`jailbreak_success` in the CSVs). These numbers are unreliable for the reasons under *Known issues*.

| Model | Rule-based ASR (%) |
|---|---|
| Llama-3.1-8B | 40.8 |
| Mistral-7B | 39.6 |
| Llama-3.2-3B | 39.6 |
| Qwen2.5-7B | 22.4 |
| Gemma2-9B | 18.4 |
| Llama-3-8B | 16.8 |
| Phi-4-14B | 11.2 |

Under the rule-based judge, Llama-3.1-8B appears most vulnerable and Llama-3-8B and Llama-3.1-8B appear far apart. Under the content judge they do not differ (17.2% vs 18.4%, p = 0.73). The paper treats the rule-based gap as a judge artefact.

Agreement between the two judges: 84%, κ = 0.60.

---

## Defense results (first 10 obfuscation + first 10 roleplay prompts per model)

**Scored with the rule-based judge only.** Reductions are against matched no-defense runs on the same 20 prompts.

| Defense | Mistral-7B (baseline 50%) | Llama-3.1-8B (baseline 45%) |
|---|---|---|
| Keyword blacklist | 35% (−15 pp) | 25% (−20 pp) |
| Self-reminder | 10% (−40 pp) | 5% (−40 pp) |
| Paraphrase | 60% (+10 pp; 12 vs 10 of 20 prompts) | 5% (−40 pp) |
| Perplexity filter | 50% (0 pp) | 45% (0 pp) |

Benign prompts (10 per model): the keyword, paraphrase, and perplexity filters blocked 0 of 10. The self-reminder benign refusal rate was **not measured**.

---

## Known issues

1. **The primary judge is unvalidated.** Its harm labels are mostly PARTIAL rather than HARMFUL (464 PARTIAL vs 45 HARMFUL). Human validation of a sample is pending.
2. **The rule-based judge has defects.** Its refusal list matches only straight apostrophes, so at least 80 of the 472 "successes" are refusals written with curly apostrophes (49 from Llama-3.1-8B, 31 from Llama-3.2-3B). Its length rule counts many confused decodings as successes. Correcting only the apostrophes raised Mistral-7B from 40% to 84%, so keyword rules cannot measure harm reliably.
3. **Llama Guard 3 is not usable** in this setup. It flags most clear refusals as unsafe, so it is not used.
4. **Responses are stored truncated to 500 characters.** The content judge sees only that excerpt.
5. **Defenses are scored with the rule-based judge and tested on 10 prompts per family and two models.**
6. **Generation was not seeded and the Ollama version was not recorded.**
7. **Pairwise tests are uncorrected** for multiple comparisons.
8. **Latency comparisons come from one sequential run.** Differences of about a second are within run-order variation.

---

## Reproducing

Scripts read and write a project folder. Set `BASE` at the top of each script to your copy of this repository, or keep the layout above and run from the repository root.

```bash
pip install pandas numpy scipy matplotlib

ollama pull llama3:8b
ollama pull llama3.1:8b
ollama pull llama3.2:3b
ollama pull mistral
ollama pull qwen2.5:7b
ollama pull gemma2:9b
ollama pull phi4:14b

python scripts/phase1_expanded.py      # main run, 1,750 generations (several hours)
python scripts/judge_validation_v2.py  # content judge (GPU recommended)
python scripts/phase3_defenses.py      # defense run (rule-based)
python scripts/rejudge_expanded.py     # rule-based re-scoring
python scripts/make_all_figures.py     # all five figures
```

The main run and the judge both save progress and can be resumed. Expect the main run to take a few hours on a recent consumer GPU.

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
```

---

## Licence

MIT. See `LICENSE`.

## Contact

Md. Robiul Islam Niloy, Department of Computer Science and Engineering, BRAC University, Dhaka, Bangladesh.
md.niloy26643@gmail.com · github.com/Mdniloykhan
