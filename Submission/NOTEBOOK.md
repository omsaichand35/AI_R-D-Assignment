# NOTEBOOK.md

# AI Team Intern Assignment

This notebook records the investigation chronologically. It documents every major hypothesis, experiment, observation, revision, and conclusion during the audit.

---

# Assignment Understanding

## Goal

The objective of the assignment is not to improve the implementation but to determine whether the conclusions presented in `REPORT_v0.md` are supported by evidence.

Every technical claim should be backed by experiments rather than assumptions.

---

# Initial Review

## Files Reviewed

- `fertility.py`
- `REPORT_v0.md`
- `model_spec.md`
- `bench_log.csv`
- English sample corpus
- Hindi sample corpus

## Initial Hypothesis

The benchmark likely contains:

- implementation issues,
- statistical weaknesses,
- conceptual mistakes,

rather than simple programming bugs.

---

# AI-Assisted Review

Three independent AI systems were used to generate candidate hypotheses.

Models used:

- ChatGPT
- Claude
- DeepSeek

The objective was to identify possible issues, not final answers.

## Candidate Findings

Common hypotheses included:

- per-line averaging,
- use of `split(" ")`,
- lowercasing before tokenization,
- extremely small evaluation corpus,
- inappropriate normalization denominator,
- tokenizer vocabulary bias.

Several additional suggestions were noted for later investigation but were not immediately accepted.

---

# Baseline Reproduction

## Hypothesis

The original benchmark should be reproducible before any modifications are made.

## Experiment

Executed the original benchmark exactly as provided.

## Observation

Successfully reproduced the reported tokenizer fertility values.

| Language | Tokens / Word |
|-----------|--------------:|
| English | 1.27 |
| Hindi | 7.45 |

The reported ratio of approximately **5.89×** matched the original report.

## Conclusion

The benchmark environment was correctly configured.

---

# Experiment 1

## Hypothesis

Per-line averaging may bias corpus-level fertility.

## Experiment

Modified the aggregation strategy to compute corpus-level fertility instead of averaging sentence-level fertility.

## Observation

Measured the difference between the two aggregation methods.

## Conclusion

Aggregation strategy influences reported fertility and should be documented explicitly.

---

# Experiment 2

## Hypothesis

Using `split(" ")` instead of `split()` could affect word counting.

## Experiment

Modified the implementation and reran the benchmark.

## Observation

Compared fertility values before and after the modification.

## Conclusion

The impact depends on corpus formatting and whitespace consistency.

---

# Experiment 3

## Hypothesis

Automatic lowercasing changes tokenizer behaviour.

## Experiment

Removed lowercasing and repeated the benchmark.

## Observation

English tokenization changed while Indic languages showed little or no change.

## Conclusion

Preprocessing is asymmetric across writing systems.

---

# Corpus Expansion

## Motivation

The original benchmark uses only two languages and a very small evaluation corpus.

## Action

Constructed a multilingual benchmark containing:

- English
- Hindi
- Bengali
- Telugu
- Tamil
- Marathi

## Observation

Tokenizer fertility varies significantly across Indic languages.

## Revision

The original benchmark should not be generalized from only English and Hindi.

---

# Multiple Tokenizer Evaluation

## Hypothesis

Observed token inflation may be caused by tokenizer design rather than language.

## Experiment

Benchmarked:

- GPT-2
- GPT-4o (`o200k_base`)
- Sarvam AI tokenizer

## Observation

Modern multilingual tokenizers significantly reduced token inflation.

Sarvam AI produced near parity between English and Hindi.

## Conclusion

Tokenizer selection substantially influences measured fertility.

---

# Denominator Evaluation

## Question

Which denominator should drive routing decisions?

Evaluated:

- Tokens per word
- Tokens per Unicode character
- Tokens per UTF-8 byte

## Observation

Each denominator measures a different property.

- Tokens per word is affected by language morphology.
- Tokens per character provides more stable cross-language comparisons.
- Tokens per byte primarily measures compression efficiency.

## Revision

A semantics-preserving denominator (such as tokens per parallel sentence) would be preferable for routing analysis.

---

# Serving Analysis

## Objective

Understand the serving benchmark using the provided model specification and benchmark logs.

Tasks performed:

- KV-cache calculation
- Maximum concurrency estimation
- Throughput analysis
- Scheduler behaviour analysis

---

# Deployment Strategy Evaluation

Three deployment strategies were evaluated:

- Supervised Fine-Tuning
- Inference-time rewriting model
- Prompt engineering

The inference-time rewriting model was selected because it best satisfied the engineering constraints, deployment timeline, reviewer availability, and implementation risk.

---

# Rejected Hypotheses

Several AI-generated observations were investigated but ultimately rejected.

Examples include:

- missing dependency handling,
- MacOS metadata files,
- runtime robustness concerns unrelated to benchmark validity.

These findings were outside the scope of the assignment and therefore excluded from the final report.

---

# Final Reflection

The investigation showed that the largest weaknesses in the original report were not programming errors but assumptions used to interpret the benchmark.

Using multiple tokenizers, multiple languages, and multiple normalization strategies produced a significantly more reliable understanding of tokenizer behaviour than the original GPT-2 bilingual benchmark.

The workflow followed throughout the assignment was:

```
Hypothesis
      ↓
Experiment
      ↓
Measurement
      ↓
Revision
      ↓
Conclusion
```

This process ensured that every accepted finding was supported by experimental evidence rather than intuition or AI-generated suggestions.