#!/usr/bin/env python3
import argparse
import csv
import math
import os
from collections import defaultdict


def parse_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_stats(stats_path):
    if not os.path.exists(stats_path):
        raise FileNotFoundError(f"Missing file: {stats_path}")

    total_row = None
    rows_by_name = {}

    with open(stats_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name", "").strip()
            req_type = row.get("Type", "").strip()
            key = f"{req_type} {name}".strip()

            if req_type == "Aggregated" and name == "":
                total_row = row
                continue

            rows_by_name[key] = row

    if total_row is None:
        raise ValueError(f"Could not find aggregated row in: {stats_path}")

    return total_row, rows_by_name


def metric_bundle(row):
    num_requests = parse_float(row.get("Request Count"))
    num_failures = parse_float(row.get("Failure Count"))
    p50 = parse_float(row.get("50%"))
    p95 = parse_float(row.get("95%"))
    p99 = parse_float(row.get("99%"))
    avg = parse_float(row.get("Average Response Time"))

    failure_rate = (num_failures / num_requests * 100.0) if num_requests > 0 else 0.0

    return {
        "requests": num_requests,
        "failures": num_failures,
        "failure_rate_pct": failure_rate,
        "avg_ms": avg,
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
    }


def pct_delta(new_value, baseline_value):
    if baseline_value == 0:
        if new_value == 0:
            return 0.0
        return math.inf
    return ((new_value - baseline_value) / baseline_value) * 100.0


def print_delta_line(metric_name, baseline_value, otel_value, lower_is_better=True, unit=""):
    delta = pct_delta(otel_value, baseline_value)
    if math.isinf(delta):
        delta_str = "inf"
    else:
        delta_str = f"{delta:+.2f}%"

    direction = "better" if (delta < 0 and lower_is_better) or (delta > 0 and not lower_is_better) else "worse"
    if math.isinf(delta):
        direction = "worse"

    unit_suffix = unit
    print(
        f"  {metric_name}: base={baseline_value:.2f}{unit_suffix} "
        f"otel={otel_value:.2f}{unit_suffix} delta={delta_str} ({direction})"
    )


def print_bundle(title, base_bundle, otel_bundle):
    print(f"\n== {title} ==")
    print_delta_line("requests", base_bundle["requests"], otel_bundle["requests"], lower_is_better=False)
    print_delta_line("failures", base_bundle["failures"], otel_bundle["failures"], lower_is_better=True)
    print_delta_line(
        "failure_rate", base_bundle["failure_rate_pct"], otel_bundle["failure_rate_pct"], lower_is_better=True, unit="%"
    )
    print_delta_line("avg", base_bundle["avg_ms"], otel_bundle["avg_ms"], lower_is_better=True, unit="ms")
    print_delta_line("p50", base_bundle["p50_ms"], otel_bundle["p50_ms"], lower_is_better=True, unit="ms")
    print_delta_line("p95", base_bundle["p95_ms"], otel_bundle["p95_ms"], lower_is_better=True, unit="ms")
    print_delta_line("p99", base_bundle["p99_ms"], otel_bundle["p99_ms"], lower_is_better=True, unit="ms")


def top_endpoints_by_volume(rows, limit):
    sortable = []
    for key, row in rows.items():
        sortable.append((parse_float(row.get("Request Count")), key))
    sortable.sort(reverse=True)
    return [key for _, key in sortable[:limit]]


def main():
    parser = argparse.ArgumentParser(description="Compare two Locust stats CSVs (baseline vs OTel).")
    parser.add_argument("--baseline", required=True, help="Path to baseline *_stats.csv")
    parser.add_argument("--otel", required=True, help="Path to OTel *_stats.csv")
    parser.add_argument("--top", type=int, default=10, help="How many top endpoints by volume to compare")
    args = parser.parse_args()

    base_total_row, base_rows = load_stats(args.baseline)
    otel_total_row, otel_rows = load_stats(args.otel)

    base_total = metric_bundle(base_total_row)
    otel_total = metric_bundle(otel_total_row)

    print("Locust Run Comparison")
    print(f"  baseline: {args.baseline}")
    print(f"  otel:     {args.otel}")

    print_bundle("Global", base_total, otel_total)

    candidate_keys = top_endpoints_by_volume(base_rows, args.top)
    print("\n== Per-endpoint (top by baseline volume) ==")

    for key in candidate_keys:
        if key not in otel_rows:
            print(f"\n- {key}")
            print("  missing in otel run")
            continue

        base_bundle = metric_bundle(base_rows[key])
        otel_bundle = metric_bundle(otel_rows[key])

        print(f"\n- {key}")
        print_delta_line("requests", base_bundle["requests"], otel_bundle["requests"], lower_is_better=False)
        print_delta_line("p95", base_bundle["p95_ms"], otel_bundle["p95_ms"], lower_is_better=True, unit="ms")
        print_delta_line("p99", base_bundle["p99_ms"], otel_bundle["p99_ms"], lower_is_better=True, unit="ms")
        print_delta_line(
            "failure_rate", base_bundle["failure_rate_pct"], otel_bundle["failure_rate_pct"], lower_is_better=True, unit="%"
        )


if __name__ == "__main__":
    main()
