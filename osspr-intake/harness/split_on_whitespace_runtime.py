#!/usr/bin/env python3
"""Runtime of split_on_whitespace on one long document.

Filters call this with newlines and tabs enabled (get_words_from_document's
defaults). The document mixes prose lines and a few tab-separated fields,
which is the same split the word-level filters run on web text. Reports
milliseconds for one call.
"""

import gc
import json
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from loguru import logger

logger.remove()

from data_juicer.ops.common.helper_func import split_on_whitespace

RUNS = 5
WORDS = (
    "the of and to in a is that for it as was with on be by this are or from "
    "at which but not we an they have has been were their its more can will "
    "about into than then some other time only first water people year day "
    "work system data model text sample document line word number result"
).split()


def build_document(num_lines=100000, seed=20261110):
    rng = random.Random(seed)
    lines = []
    for index in range(num_lines):
        if index % 40 == 0:
            lines.append(f"field{index}\tvalue{index}\tnote")
        else:
            tokens = [rng.choice(WORDS) for _ in range(18)]
            lines.append(" ".join(tokens))
    return "\n".join(lines)


def main():
    document = build_document()
    for _ in range(2):
        split_on_whitespace(document, new_line=True, tab=True)
    runs = []
    for _ in range(RUNS):
        gc.collect()
        start = time.perf_counter()
        split_on_whitespace(document, new_line=True, tab=True)
        runs.append((time.perf_counter() - start) * 1000.0)
    median = statistics.median(runs)
    noise = (max(runs) - min(runs)) / median * 100.0
    print(
        json.dumps(
            {
                "function": "split_on_whitespace",
                "metric": "runtime_ms",
                "chars": len(document),
                "runs_ms": [round(value, 4) for value in runs],
                "baseline_median_ms": round(median, 4),
                "baseline_noise_pct": round(noise, 4),
            }
        )
    )


if __name__ == "__main__":
    main()
