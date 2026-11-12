"""Baseline for WhitespaceNormalizationMapper.process_batched.

Prose with ordinary spaces, newlines, and occasional non-breaking spaces.
The mapper still inspects every character.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data_juicer.ops.mapper.whitespace_normalization_mapper import WhitespaceNormalizationMapper

from timing import measure

WORDS = (
    "the",
    "model",
    "processes",
    "documents",
    "and",
    "keeps",
    "quality",
    "high",
    "across",
    "batches",
)


def build_text():
    parts = []
    for i in range(420_000):
        piece = WORDS[i % len(WORDS)]
        if i % 70 == 0:
            piece += "\u00a0"
        if i % 50 == 0:
            piece += "\n"
        parts.append(piece)
    return " ".join(parts)


def main():
    text = build_text()
    op = WhitespaceNormalizationMapper()

    def call():
        op.process_batched({"text": [text]})

    median, noise, runs = measure(call)
    json.dump(
        {
            "function": "WhitespaceNormalizationMapper.process_batched",
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
