# Part B1 - KV Cache Capacity Reconciliation

## Objective

The objective of this section is to determine:

1. The exact KV-cache memory required **per generated token**.
2. The theoretical maximum number of concurrent **4096-token sequences** that can fit on the target GPU.
3. Whether the theoretical calculation agrees with the observed benchmark logs.

This analysis is performed **only using the provided model specification**, before consulting the benchmark logs.

---

# Model Specification

| Property | Value |
|-----------|------:|
| Model | FLM-4B-Instruct |
| Layers | 28 |
| Hidden Dimension | 3072 |
| Query Heads | 24 |
| KV Heads (GQA) | 8 |
| Head Dimension | 128 |
| KV Precision | FP16 |
| GPU | NVIDIA L4 (24 GB) |
| GPU Memory Utilization | 92% |
| Runtime Overhead | 1.6 GB |

---

# Step 1 — KV Cache Memory per Token

For every generated token, each transformer layer stores:

- Key vectors
- Value vectors

Each vector contains

```
KV Heads × Head Dimension
```

elements.

Therefore,

```
Elements per token per layer

=
2 × KV_heads × head_dim
```

Substituting the model values:

```
=
2 × 8 × 128

=
2048 FP16 values
```

Since FP16 occupies **2 bytes**,

```
Bytes per token per layer

=
2048 × 2

=
4096 bytes
```

---

# Step 2 — KV Cache Across All Layers

The model contains

```
28 layers
```

Therefore,

```
KV Cache per Token

=
4096 × 28

=
114,688 bytes
```

or approximately

```
112 KB per token
```

---

# Step 3 — Available KV Cache Memory

Total GPU memory

```
24 GB
```

Configured GPU utilization

```
92%
```

Available GPU memory

```
24 × 0.92

=
22.08 GB
```

Runtime overhead

```
1.6 GB
```

Remaining memory available for KV cache

```
22.08 − 1.6

=
20.48 GB
```

---

# Step 4 — Maximum Cached Tokens

Convert available memory into bytes

```
20.48 GB

≈

20.48 × 1024³

≈

21,990,232,555 bytes
```

Maximum cached tokens

```
21,990,232,555

÷

114,688

≈

191,740 tokens
```

---

# Step 5 — Maximum Concurrent 4096-Token Sequences

Each request occupies

```
4096 tokens
```

Therefore,

```
191,740

÷

4096

≈

46.8
```

The GPU can therefore hold approximately

```
46 concurrent 4096-token sequences
```

before exhausting KV-cache memory.

---

# Interpretation

The theoretical analysis predicts that the system should begin experiencing memory pressure once the number of simultaneously active long-context requests approaches **46 sequences**.

Consequently, larger batches should begin to exhibit:

- scheduler preemption,
- reduced throughput,
- increased latency, and
- KV-cache saturation.

These predictions will be validated against the benchmark logs in the following sections.

---

# Final Answers

## (a) KV Cache Bytes per Token

```
114,688 bytes

≈

112 KB per token
```

---

## (b) Maximum Concurrent 4096-Token Sequences

```
≈46 sequences
```

---

# Preliminary Conclusion

The theoretical KV-cache calculation indicates that a 24 GB NVIDIA L4 GPU configured with 92% memory utilization can simultaneously accommodate approximately **46 full-length (4096-token) sequences**.

If the benchmark log shows scheduler preemption or throughput degradation near this point, the observed behavior is consistent with the hardware limits rather than an implementation defect.