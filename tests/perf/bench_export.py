"""Benchmark the export pipeline on real data (not part of the test suite).

Example::

    uv run python tests/perf/bench_export.py "C:/Exports/Profiles" \\
        --xpath "//field/filter/@id" --xpath "//field[filter]/@name" --workers 1 4 8 16

Reports wall time and peak traced memory per worker count, so the thread count
(and whether processes would help at all) is decided on measurements.
"""

from __future__ import annotations

import argparse
import tempfile
import time
import tracemalloc
from pathlib import Path

from xmluvation.application.cancellation import CancellationToken, NullReporter
from xmluvation.application.export_xpath_csv import make_spec, run_export


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("folder", type=Path)
    parser.add_argument("--xpath", action="append", required=True)
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 4, 8])
    parser.add_argument("--group", action="store_true")
    parser.add_argument("--memory", action="store_true", help="trace peak memory (slower)")
    args = parser.parse_args()

    headers = ", ".join(f"C{i}" for i in range(len(args.xpath)))
    with tempfile.TemporaryDirectory() as tmp:
        for workers in args.workers:
            out = Path(tmp) / f"bench_{workers}.csv"
            spec = make_spec(str(args.folder), args.xpath, headers, str(out), args.group, workers)
            if args.memory:
                tracemalloc.start()
            started = time.perf_counter()
            result = run_export(spec, NullReporter(), CancellationToken())
            elapsed = time.perf_counter() - started
            peak = (
                f", peak {tracemalloc.get_traced_memory()[1] / 1e6:7.1f} MB" if args.memory else ""
            )
            if args.memory:
                tracemalloc.stop()
            print(
                f"workers={workers:>3}: {elapsed:7.2f} s, {result.processed_files} files, "
                f"{result.rows_written} rows, {len(result.errors)} errors{peak}"
            )


if __name__ == "__main__":
    main()
