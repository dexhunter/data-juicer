#!/usr/bin/env python3
"""Peak Python memory of DocumentMinhashDeduplicator.compute_hash.

The sample is one long space-tokenized document, the default MinHash path
(tokenization='space', 5-word shingles, 256 permutations). Peak is
tracemalloc's high-water mark for one call, in bytes. Bands are fixed so
init does not run the scipy parameter search; that search is not part of
compute_hash.
"""

import gc
import json
import random
import statistics
import sys
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from loguru import logger

logger.remove()

from data_juicer.ops.deduplicator.document_minhash_deduplicator import (
    DocumentMinhashDeduplicator,
)

RUNS = 5


def build_document(num_tokens=25000, vocab=6000, seed=20261110):
    rng = random.Random(seed)
    words = [f"w{index:05d}" for index in range(vocab)]
    return " ".join(rng.choice(words) for _ in range(num_tokens))


def main():
    text = build_document()
    op = DocumentMinhashDeduplicator(
        tokenization="space",
        window_size=5,
        lowercase=True,
        num_permutations=256,
        num_bands=20,
        num_rows_per_band=12,
    )
    op.compute_hash({"text": text})
    peaks = []
    for _ in range(RUNS):
        gc.collect()
        tracemalloc.start()
        tracemalloc.reset_peak()
        op.compute_hash({"text": text})
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peaks.append(peak)
    median = statistics.median(peaks)
    noise = (max(peaks) - min(peaks)) / median * 100.0
    print(
        json.dumps(
            {
                "function": "DocumentMinhashDeduplicator.compute_hash",
                "metric_kind": "peak_memory_bytes",
                "chars": len(text),
                "runs": peaks,
                "baseline_value": median,
                "baseline_noise_pct": round(noise, 4),
            }
        )
    )


if __name__ == "__main__":
    main()
