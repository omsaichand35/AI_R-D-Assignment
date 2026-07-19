#!/usr/bin/env python3
"""
fertility.py -- tokenizer fertility benchmark (v0)

Computes tokenizer fertility (tokens per word) and compression
(tokens per character) for one or more language corpora.

Usage:
    python fertility.py --corpus eng=corpus_sample/eng_sample.txt \
                        --corpus hin=corpus_sample/hin_sample.txt \
                        --tokenizer gpt2

Tokenizers:
    gpt2            -> tiktoken "gpt2" encoding (default)
    hf:<repo_id>    -> any HuggingFace tokenizer, e.g. hf:xlm-roberta-base

Author: previous intern (v0, "good enough for the deck")
"""

import argparse
import os
import random
import sys
import unicodedata

random.seed(1337)  # reproducibility


def load_tokenizer(spec: str):
    if spec.startswith("hf:"):
        if "pyarrow" not in sys.modules:
            try:
                import pyarrow
            except ImportError:
                sys.modules["pyarrow"] = None
        from transformers import AutoTokenizer

        tok = AutoTokenizer.from_pretrained(spec[3:])
        return lambda s: tok.encode(s, add_special_tokens=False)
    else:
        import tiktoken

        enc = tiktoken.get_encoding(spec)
        return enc.encode


def read_lines(path: str, max_lines: int = 100, streaming: bool = True):
    if os.path.exists(path):
        lines = []
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                # normalize just in case -- some corpora are messy
                line = unicodedata.normalize("NFC", line)
                lines.append(line)
                if max_lines and len(lines) >= max_lines:
                    break
        return lines
    else:
        try:
            from datasets import load_dataset

            # Load subset of IndicCorpV2 (e.g., data_dir="data/tel_Telu")
            dataset = load_dataset("ai4bharat/IndicCorpV2", "indiccorp_v2", data_dir=path, streaming=streaming)
            split = dataset["train"] if (hasattr(dataset, "keys") and "train" in dataset) else dataset
            lines = []
            for item in split:
                raw = item.get("text", "")
                if isinstance(raw, str):
                    line = raw.strip()
                    if not line:
                        continue
                    line = unicodedata.normalize("NFC", line)
                    lines.append(line)
                    if max_lines and len(lines) >= max_lines:
                        break
            return lines
        except Exception:
            # Fallback to pure-HTTP streaming from HuggingFace Hub if datasets/pyarrow is blocked or errors
            from huggingface_hub import hf_hub_url
            import urllib.request

            fname_map = {
                "tel_telu": "data/te.txt",
                "hin_deva": "data/hi-1.txt",
                "ben_beng": "data/bn.txt",
                "tam_taml": "data/ta.txt",
                "mar_deva": "data/mr.txt",
                "guj_gujr": "data/gu.txt",
                "kan_knda": "data/kn.txt",
                "mal_mlym": "data/ml.txt",
                "pan_guru": "data/pa.txt",
                "ori_orya": "data/or.txt",
                "eng_latn": "data/en.txt",
                "eng": "data/en.txt",
                "en": "data/en.txt",
            }
            clean_path = path.lower().replace("data/", "")
            filename = fname_map.get(clean_path, path if path.endswith(".txt") else f"data/{clean_path[:2]}.txt")

            url = hf_hub_url("ai4bharat/IndicCorpV2", filename=filename, repo_type="dataset")
            lines = []
            with urllib.request.urlopen(url) as req:
                for raw_bytes in req:
                    line = raw_bytes.decode("utf-8", errors="ignore").strip()
                    if not line:
                        continue
                    line = unicodedata.normalize("NFC", line)
                    lines.append(line)
                    if max_lines and len(lines) >= max_lines:
                        break
            return lines


def analyze(lines, encode):
    """Return (fertility, tokens_per_char, tokens_per_byte) averaged over lines."""
    per_line_fertility = []
    per_line_tpc = []
    per_line_tpb = []
    for line in lines:
        tokens = encode(line)
        words = line.split()
        chars = len(line)
        num_bytes = len(line.encode("utf-8"))
        per_line_fertility.append(len(tokens) / len(words) if words else 0.0)
        per_line_tpc.append(len(tokens) / chars if chars else 0.0)
        per_line_tpb.append(len(tokens) / num_bytes if num_bytes else 0.0)
    n = len(per_line_fertility)
    if n == 0:
        return 0.0, 0.0, 0.0
    return sum(per_line_fertility) / n, sum(per_line_tpc) / n, sum(per_line_tpb) / n


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--corpus",
        action="append",
        required=True,
        metavar="LANG=PATH",
        help="language code and path/data_dir, e.g. eng=data/eng.txt or tel=data/tel_Telu (repeatable)",
    )
    ap.add_argument(
        "--tokenizer",
        action="append",
        help="tokenizer spec, e.g. gpt2, cl100k_base, o200k_base, or hf:<repo_id> (repeatable)",
    )
    ap.add_argument(
        "--max-lines",
        type=int,
        default=100,
        help="maximum number of lines to analyze per corpus (default: 100)",
    )
    ap.add_argument(
        "--no-streaming",
        action="store_true",
        help="disable streaming for HuggingFace datasets",
    )
    args = ap.parse_args()

    tokenizers = args.tokenizer if args.tokenizer else ["gpt2"]

    # Read lines once for all corpora to avoid re-fetching across tokenizers
    corpus_lines = {}
    for spec in args.corpus:
        lang, path = spec.split("=", 1)
        corpus_lines[lang] = read_lines(path, max_lines=args.max_lines, streaming=not args.no_streaming)

    for i, tok_spec in enumerate(tokenizers):
        if i > 0:
            print("\n" + "=" * 50 + "\n")
        encode = load_tokenizer(tok_spec)
        print(f"tokenizer: {tok_spec}")
        print(f"{'lang':<8}{'tok/word':>14}{'tok/char':>14}{'tok/byte':>14}")
        print("-" * 50)
        results = {}
        for lang, lines in corpus_lines.items():
            fert, tpc, tpb = analyze(lines, encode)
            results[lang] = (fert, tpc, tpb)
            print(f"{lang:<8}{fert:>14.2f}{tpc:>14.3f}{tpb:>14.3f}")

        if len(results) >= 2:
            langs = list(results)
            base = langs[0]
            print(f"\nComparison ratios relative to {base}:")
            for lang in langs[1:]:
                ratio_w = results[lang][0] / results[base][0] if results[base][0] else 0.0
                ratio_c = results[lang][1] / results[base][1] if results[base][1] else 0.0
                ratio_b = results[lang][2] / results[base][2] if results[base][2] else 0.0
                status = "worse" if ratio_w > 1 else "better"
                print(
                    f"  {lang:<6} -> tok/word ratio: {ratio_w:>5.2f}x | "
                    f"tok/char ratio: {ratio_c:>5.2f}x | "
                    f"tok/byte ratio: {ratio_b:>5.2f}x ({status} tokenization)"
                )


if __name__ == "__main__":
    main()
