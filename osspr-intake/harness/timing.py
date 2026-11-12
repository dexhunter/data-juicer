"""Shared wall-clock timing for intake baselines."""

import statistics
import time


def measure(fn, repeats=7, warmup=1):
    """Return median milliseconds and relative spread over ``repeats`` calls.

    Spread is ``(max - min) / median * 100`` after ``warmup`` untimed calls.
    """
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000.0)
    median = statistics.median(samples)
    noise = (max(samples) - min(samples)) / median * 100.0 if median else 0.0
    return median, noise, samples
