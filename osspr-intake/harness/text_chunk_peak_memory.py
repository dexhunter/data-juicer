#!/usr/bin/env python3
"""Peak Python memory of TextChunkMapper.recursively_chunk on one long article.

The article is paragraph-broken prose, the shape this mapper sees when a
training pipeline chunks web or wiki text with both max_len and a blank-line
split. Peak is tracemalloc's high-water mark for one call, in bytes.
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

from data_juicer.ops.mapper.text_chunk_mapper import TextChunkMapper

RUNS = 5
MAX_LEN = 1000
WORDS = (
    "the of and to in a is that for it as was with on be by this are or from "
    "at which but not we an they have has been were their its more can will "
    "about into than then some other time only first water people year day "
    "work system data model text sample document line word number result"
).split()


def build_article(num_paragraphs=900, words_per_paragraph=70, seed=20261110):
    rng = random.Random(seed)
    paragraphs = []
    for index in range(num_paragraphs):
        tokens = [rng.choice(WORDS) for _ in range(words_per_paragraph)]
        tokens[0] = tokens[0].capitalize()
        paragraphs.append(" ".join(tokens) + f" ({index}).")
    return "\n\n".join(paragraphs)


def main():
    text = build_article()
    op = TextChunkMapper(max_len=MAX_LEN, split_pattern=r"\n\n", overlap_len=0)
    op.recursively_chunk(text)  # warmup: compile the split pattern
    peaks = []
    for _ in range(RUNS):
        gc.collect()
        tracemalloc.start()
        tracemalloc.reset_peak()
        op.recursively_chunk(text)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peaks.append(peak)
    median = statistics.median(peaks)
    noise = (max(peaks) - min(peaks)) / median * 100.0
    print(
        json.dumps(
            {
                "function": "TextChunkMapper.recursively_chunk",
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
