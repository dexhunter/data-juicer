"""Baseline for CleanIpMapper.process_batched.

Ordinary prose that contains colons (common in English) plus two IPv4
literals. The default pattern also searches for compressed IPv6.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data_juicer.ops.mapper.clean_ip_mapper import CleanIpMapper

from timing import measure

SENTENCE = "The plant employs workers and the mayor said: production continued overnight. "


def build_text():
    return SENTENCE * 8000 + " Gateway 10.1.2.3 and backup 192.168.0.10 are documented. "


def main():
    text = build_text()
    op = CleanIpMapper()

    def call():
        op.process_batched({"text": [text]})

    median, noise, runs = measure(call)
    json.dump(
        {
            "function": "CleanIpMapper.process_batched",
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
