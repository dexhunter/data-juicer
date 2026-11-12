"""Baseline for PiiRedactionMapper._redact_text.

Same shape of prose as the clean-ip benchmark, plus one email, one URL,
and one IPv4 so the redactor both scans and rewrites. Defaults leave the
extended masks on (URLs, IPs, MAC, PEM, JWT).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data_juicer.ops.mapper.pii_redaction_mapper import PiiRedactionMapper

from timing import measure

SENTENCE = "The plant employs workers and the mayor said: production continued overnight. "


def build_text():
    prose = SENTENCE * 8000
    return prose + " mail alice@example.com and see https://example.com/a and host 10.2.3.4 "


def main():
    text = build_text()
    op = PiiRedactionMapper()

    def call():
        op._redact_text(text)

    median, noise, runs = measure(call)
    json.dump(
        {
            "function": "PiiRedactionMapper._redact_text",
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
