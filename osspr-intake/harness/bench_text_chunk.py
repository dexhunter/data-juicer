"""Baseline for TextChunkMapper.recursively_chunk.

A single 2.2MB block with no blank-line delimiter. max_len=4096 and
overlap_len=256 force a hard cut on every step, which is the path that
copies the remaining tail and recurses.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data_juicer.ops.mapper.text_chunk_mapper import TextChunkMapper

from timing import measure


def build_text():
    unit = "The quick brown fox jumps over the lazy dog. " * 30
    repeats = 2_200_000 // len(unit) + 1
    return (unit * repeats)[:2_200_000]


def main():
    text = build_text()
    op = TextChunkMapper(max_len=4096, overlap_len=256, split_pattern=r"\n\n")

    def call():
        op.recursively_chunk(text)

    median, noise, runs = measure(call)
    json.dump(
        {
            "function": "TextChunkMapper.recursively_chunk",
            "chars": len(text),
            "median_ms": round(median, 2),
            "noise_pct": round(noise, 2),
            "runs_ms": [round(v, 2) for v in runs],
        },
        sys.stdout,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
