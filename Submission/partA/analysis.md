# A3. Corrected Analysis and Denominator Reasoning

## Objective

The original report compared only English and Hindi using the GPT-2 tokenizer and concluded that Hindi requires approximately 5.9× more tokens than English. This conclusion was then used to estimate serving cost and recommend routing all Indic traffic to an Indic-specialized tokenizer.

To verify whether this conclusion generalizes, the benchmark was extended in two dimensions:

1. **Tokenizer diversity**
   - GPT-4o (`o200k_base`)
   - Sarvam AI (`sarvamai/sarvam-2b`)

2. **Language diversity**
   - English
   - Hindi
   - Bengali
   - Telugu
   - Tamil
   - Marathi

Additionally, instead of relying only on **tokens per word**, two additional normalization strategies were evaluated:

- Tokens per Unicode character
- Tokens per UTF-8 byte

---

# Corrected Cross-Language Analysis

## GPT-2 Baseline

The original benchmark reported:

| Language | Tokens / Word |
|-----------|--------------:|
| English | 1.27 |
| Hindi | 7.45 |

This corresponds to approximately **5.89×** more tokens per word for Hindi than English. :contentReference[oaicite:0]{index=0}

While this result is reproducible, it represents only a single tokenizer evaluated on a very small bilingual corpus.

---

# GPT-4o Tokenizer (o200k_base)

| Language | Tok/Word | Tok/Char | Tok/Byte |
|-----------|---------:|---------:|----------:|
| English | 1.39 | 0.223 | 0.222 |
| Hindi | 1.62 | 0.321 | 0.125 |
| Bengali | 2.52 | 0.384 | 0.145 |
| Telugu | 3.35 | 0.413 | 0.153 |
| Tamil | 3.46 | 0.372 | 0.139 |
| Marathi | 2.75 | 0.392 | 0.147 |

### Observations

Compared with GPT-2, GPT-4o dramatically reduces token inflation for Indic languages.

Instead of Hindi requiring nearly six times as many tokens as English, the ratio decreases to only **1.16×** at the word level.

Character-level ratios remain relatively close across languages (approximately 1.4–1.8×), suggesting that much of the apparent inflation observed with GPT-2 originates from tokenizer vocabulary rather than the writing system itself.

Byte-level normalization produces ratios below one because Indic characters occupy multiple UTF-8 bytes. Consequently, each token represents substantially more encoded bytes than English.

---

# Sarvam AI Tokenizer

| Language | Tok/Word | Tok/Char | Tok/Byte |
|-----------|---------:|---------:|----------:|
| English | 1.72 | 0.274 | 0.273 |
| Hindi | 1.41 | 0.279 | 0.109 |
| Bengali | 2.14 | 0.325 | 0.122 |
| Telugu | 2.75 | 0.339 | 0.125 |
| Tamil | 2.74 | 0.293 | 0.110 |
| Marathi | 2.05 | 0.294 | 0.110 |

### Observations

Sarvam AI's tokenizer demonstrates significantly improved handling of Indic scripts.

The most notable result is Hindi, which requires **0.82×** the number of tokens per word compared with English. This is the opposite of the GPT-2 result and indicates that tokenizer design has a substantial influence on measured fertility.

Character-level normalization shows near parity between English and Hindi (1.01×), while Tamil and Marathi remain close to English as well.

Byte-level measurements indicate that Sarvam packs approximately twice as many UTF-8 bytes into each token for Indic languages compared with English. This reflects higher compression efficiency for Indic scripts, although it should not be interpreted as a direct measure of semantic quality.

---

# Denominator Comparison

## 1. Tokens per Word

Advantages

- Simple and intuitive.
- Frequently reported in tokenizer literature.

Limitations

- Depends on language-specific word segmentation.
- Sensitive to morphology and writing conventions.
- Not directly comparable across all languages.

---

## 2. Tokens per Unicode Character

Advantages

- Reduces dependence on whitespace segmentation.
- Produces more stable comparisons across languages.

Limitations

- Unicode code points do not correspond to user-visible characters.
- Indic scripts use combining marks and conjuncts, making code-point counts imperfect.

---

## 3. Tokens per UTF-8 Byte

Advantages

- Measures tokenizer compression efficiency.
- Useful for storage and transmission analysis.

Limitations

- Strongly influenced by UTF-8 encoding.
- Does not directly represent semantic content.
- Lower values do not necessarily imply better language understanding.

---

# Which Metric Should Drive Routing Decisions?

The original report implicitly assumes that **tokens per word** is the appropriate metric for estimating serving cost.

This audit finds that assumption to be too simplistic.

The choice of denominator changes the interpretation substantially:

- Tokens per word exaggerates differences caused by morphology and tokenization strategy.
- Tokens per byte emphasizes encoding efficiency rather than semantic equivalence.
- Tokens per character provides a more stable comparison across alphabetic and Indic scripts but still depends on Unicode representation.

For routing and cost estimation, the denominator should hold semantic content approximately constant across languages. In practice, the most appropriate metric would be **tokens per parallel sentence** (or another meaning-preserving unit) because it compares equivalent information rather than language-specific word boundaries.

Among the three evaluated denominators, **tokens per Unicode character** provides the most balanced cross-language comparison and is therefore the preferred metric for tokenizer benchmarking. Tokens per byte should be interpreted primarily as a compression metric rather than a routing metric.

---

# Corrected Recommendation

The original recommendation to budget approximately **6×** serving cost for Hindi and route all Indic traffic to a specialized tokenizer is not supported by the broader evaluation.

The expanded benchmark demonstrates that:

- Tokenizer choice has a larger effect than initially reported.
- Modern multilingual tokenizers substantially reduce token inflation.
- Indic-specialized tokenizers can achieve tokenization efficiency comparable to English for several Indic languages.
- Routing decisions should therefore be based on measurements across multiple tokenizers and multilingual evaluation corpora rather than a single GPT-2 benchmark.