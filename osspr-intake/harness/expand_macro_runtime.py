#!/usr/bin/env python3
"""Runtime of ExpandMacroMapper.process_batched on a batch of LaTeX papers.

Each paper has a preamble of \\newcommand / \\def macros and a body that uses
them, which is the arXiv-cleaning workload this mapper was written for.
Reports milliseconds for one batched call.
"""

import gc
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from loguru import logger

logger.remove()

from data_juicer.ops.mapper.expand_macro_mapper import ExpandMacroMapper

RUNS = 5
BATCH = 24
NUM_NEWCOMMAND = 50
NUM_DEF = 20
NUM_USES = 4000


def build_paper(paper_index):
    macros = []
    names = []
    for index in range(NUM_NEWCOMMAND):
        name = f"nc{paper_index}x{index}"
        names.append(name)
        macros.append(rf"\newcommand{{\{name}}}{{expanded newcommand {index}}}")
    for index in range(NUM_DEF):
        name = f"df{paper_index}x{index}"
        names.append(name)
        macros.append(rf"\def\{name}{{expanded def {index}}}")
    uses = []
    for index in range(NUM_USES):
        name = names[index % len(names)]
        uses.append(f"Term {index} refers to \\{name} in the method.")
    return "\n".join(macros) + "\n" + " ".join(uses)


def main():
    papers = [build_paper(index) for index in range(BATCH)]
    op = ExpandMacroMapper()
    for _ in range(2):
        op.process_batched({"text": list(papers)})
    runs = []
    for _ in range(RUNS):
        samples = {"text": list(papers)}
        gc.collect()
        start = time.perf_counter()
        op.process_batched(samples)
        runs.append((time.perf_counter() - start) * 1000.0)
    median = statistics.median(runs)
    noise = (max(runs) - min(runs)) / median * 100.0
    print(
        json.dumps(
            {
                "function": "ExpandMacroMapper.process_batched",
                "metric": "runtime_ms",
                "papers": BATCH,
                "chars": sum(len(paper) for paper in papers),
                "runs_ms": [round(value, 4) for value in runs],
                "baseline_median_ms": round(median, 4),
                "baseline_noise_pct": round(noise, 4),
            }
        )
    )


if __name__ == "__main__":
    main()
