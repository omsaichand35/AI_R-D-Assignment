# A4. Recommendation Memo

**To:** Engineering Leadership  
**From:** AI Team Intern  
**Subject:** Recommendation Following Tokenizer Audit  
**Date:** July 2026

---

## Executive Summary

The original benchmark successfully reproduces the reported tokenizer fertility values; however, its conclusions should **not** be used for production routing or capacity planning without revision.

The analysis is based on only two languages (English and Hindi), a very small evaluation corpus, and a single GPT-2 tokenizer. Our expanded evaluation demonstrates that the observed token inflation is strongly dependent on tokenizer choice. Modern multilingual and Indic-specialized tokenizers reduce the gap between English and Indic languages substantially, invalidating the conclusion that Hindi inherently requires approximately six times more tokens than English.

---

## Corrected Headline Findings

- The original GPT-2 benchmark reproduces a **5.89×** higher token-per-word ratio for Hindi than English. :contentReference[oaicite:0]{index=0}

- Extending the evaluation to six languages demonstrates that tokenization efficiency varies significantly across Indic languages and should not be inferred from Hindi alone. :contentReference[oaicite:1]{index=1}

- GPT-4o's `o200k_base` tokenizer reduces Hindi's token-per-word ratio to approximately **1.16×** relative to English.

- Sarvam AI's Indic-specialized tokenizer further improves efficiency, reducing Hindi to **0.82×** the English token-per-word ratio.

- The benchmark therefore measures **tokenizer behavior as much as language behavior**. The tokenizer selected has a larger impact than suggested in the original report.

---

## Routing Recommendation

Do **not** route all Indic traffic based solely on the results of the original GPT-2 benchmark.

Instead:

1. Benchmark every production tokenizer using a multilingual evaluation corpus.
2. Compare languages using semantically equivalent parallel text.
3. Evaluate multiple normalization strategies before making capacity estimates.
4. Maintain separate benchmark reports whenever the tokenizer is changed.

Routing policies should be based on the tokenizer that will actually be deployed rather than historical GPT-2 measurements.

---

## Biggest Caveat

Although the evaluation corpus is substantially larger and more diverse than the original benchmark, it still represents only a limited set of languages and domains.

The benchmark does not evaluate:

- conversational chat,
- code-mixed text,
- domain-specific terminology,
- long-context prompts, or
- production traffic distributions.

Consequently, the reported fertility values should be treated as benchmarking estimates rather than absolute production costs.

---

## Recommended Production Metric

The single production metric I recommend monitoring is:

> **Average input tokens per request, grouped by language and tokenizer version.**

This metric directly reflects the quantity that influences context window utilization, inference latency, KV-cache usage, and serving cost.

Monitoring token counts over time also allows rapid detection of regressions caused by tokenizer updates, prompt template changes, or shifts in language distribution.

---

## Final Recommendation

The original report should **not** be accepted in its current form.

The benchmark should be updated to:

- use a multilingual evaluation corpus,
- compare multiple tokenizer families,
- report uncertainty alongside mean values,
- distinguish tokenizer effects from language effects, and
- base production routing decisions on measurements collected using the deployment tokenizer rather than GPT-2.

These changes provide a substantially stronger foundation for routing, capacity planning, and future tokenizer evaluations.