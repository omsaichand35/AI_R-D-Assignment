# Part C – Decision Memo

**To:** Product & Engineering Leadership  
**From:** AI Team Intern  
**Subject:** Recommendation for Improving Conversational Style in Indian Languages

---

# Executive Summary

After evaluating the available options under the given engineering and resource constraints, I recommend **Option (b): deploying a small inference-time rewriting model** (≤1B parameters) after the primary assistant model.

This approach provides the best balance between development effort, deployment risk, reviewer availability, and launch timeline. It allows stylistic improvements without modifying the primary model and can be iterated independently if quality issues are discovered after deployment.

---

# Problem Statement

Current responses in

- Hindi
- Kannada
- Tamil
- Telugu
- Bengali
- Marathi

sound overly formal and textbook-like.

The objective is to make responses sound natural and conversational while preserving factual correctness.

Available options:

1. Supervised Fine-Tuning (SFT)
2. Small inference-time rewriting model
3. Prompt engineering only

---

# Assumptions

The following assumptions are used throughout this analysis.

- One NVIDIA A100 (80 GB) is available for two weeks.
- One native reviewer is available for Hindi and Kannada only.
- Total review time is 10 hours per week.
- Launch review occurs in three weeks.
- No external API budget is available.
- Existing base model quality is acceptable; only style requires improvement.
- The rewriting model operates only on the final assistant response.

---

# Option Evaluation

## Option A – Supervised Fine-Tuning

### Advantages

- Best long-term quality.
- Single-model inference.
- No additional inference stage.

### Disadvantages

- Requires creation of a large supervised dataset.
- Reviewer time is insufficient for high-quality multilingual annotation.
- Higher engineering and experimentation cost.
- Higher deployment risk within three weeks.

### Assessment

Not recommended under current constraints.

---

## Option B – Inference-Time Rewriter (Recommended)

### Advantages

- Independent of the main model.
- Easy to deploy and rollback.
- Requires significantly less data.
- Can be improved iteratively.
- Minimal changes to the production system.

### Disadvantages

- Slight increase in inference latency.
- Requires maintaining two models.

### Assessment

Provides the best trade-off between engineering effort and expected quality improvement.

---

## Option C – Prompt Engineering

### Advantages

- Immediate implementation.
- No additional models.
- Zero training cost.

### Disadvantages

- Inconsistent outputs.
- Difficult to guarantee conversational style.
- Highly dependent on prompt wording.

### Assessment

Useful as a baseline but unlikely to achieve production-quality consistency.

---

# Back-of-the-Envelope Arithmetic

## Synthetic Dataset

Generate approximately

- 50,000 synthetic response pairs per language

For six languages:

```
50,000 × 6

=

300,000 examples
```

No manual annotation is required for the initial dataset.

---

## Human Review Capacity

Reviewer availability:

```
10 hours/week

×

2 weeks

=

20 hours
```

Assuming

```
100 examples/hour
```

Maximum reviewed samples:

```
20 × 100

=

2,000 examples
```

These should be used for validation and prompt refinement rather than full dataset creation.

---

## Training Cost

A ≤1B parameter rewriting model can comfortably fit on an A100 80 GB.

Expected fine-tuning time:

- Approximately 1–3 days

Remaining time:

- Evaluation
- Error analysis
- Prompt refinement
- Deployment testing

---

## Serving Cost

Additional serving cost consists of one lightweight rewriting pass.

Compared to retraining the main model, this introduces only a modest increase in latency while preserving deployment flexibility.

---

# Success Metric

The deployment will be considered successful if:

- At least **85%** of reviewed responses are judged **more conversational than the baseline** by the native reviewer.
- Less than **2%** of reviewed responses contain factual changes introduced by the rewriter.
- Average additional latency remains below **100 ms per response**.

---

# Kill Criterion

The project will be stopped if **either** of the following conditions is observed after the first week:

- Conversational quality improvement is less than **70%** in reviewer evaluations.
- More than **5%** of responses introduce factual or semantic errors.
- The latency overhead exceeds **150 ms** per response.

If any of these conditions occur, the team should abandon the rewriting model and fall back to prompt engineering for the launch.

---

# Experiment

The first experiment should compare all three approaches on the same evaluation set.

Procedure:

1. Select 200 representative prompts.
2. Generate baseline responses.
3. Apply prompt engineering.
4. Apply the rewriting model.
5. Compare outputs using the native reviewer.
6. Measure:
   - conversational naturalness,
   - factual preservation,
   - latency.

This experiment provides an early estimate of whether the rewriting model justifies further investment.

---

# Risks

- Limited reviewer coverage for only two languages.
- Synthetic data may introduce stylistic artifacts.
- Different Indian languages exhibit distinct conversational conventions.
- A style rewriter may occasionally modify factual content.

---

# Final Recommendation

Deploy a **small inference-time rewriting model** after the primary assistant model.

This option offers the best balance between engineering effort, reviewer availability, deployment risk, and expected quality improvement. It also provides the greatest flexibility: if quality is unsatisfactory, the rewriting model can be updated or removed without retraining or redeploying the primary assistant.

Given the available hardware, timeline, and review resources, this is the lowest-risk approach with the highest probability of achieving the launch objective.