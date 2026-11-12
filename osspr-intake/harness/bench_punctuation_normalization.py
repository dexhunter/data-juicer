"""Baseline for PunctuationNormalizationMapper.process_batched.

English prose with Unicode punctuation about every 40 words, including the
multi-character replacements (em dash, ellipsis, fullwidth period).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data_juicer.ops.mapper.punctuation_normalization_mapper import PunctuationNormalizationMapper

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
    "of",
    "web",
    "text",
)
UNI = ("，", "。", "：", "？", "！", "“", "”", "（", "）", "；", "、", "—", "…", "．")


def build_text():
    parts = []
    for i in range(400_000):
        piece = WORDS[i % len(WORDS)]
        if i % 40 == 0:
            piece += UNI[i % len(UNI)]
        parts.append(piece)
    return " ".join(parts)


def main():
    text = build_text()
    op = PunctuationNormalizationMapper()

    def call():
        op.process_batched({"text": [text]})

    median, noise, runs = measure(call)
    json.dump(
        {
            "function": "PunctuationNormalizationMapper.process_batched",
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
