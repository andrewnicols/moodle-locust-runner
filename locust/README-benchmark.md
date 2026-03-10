# Locust OTel A/B Benchmark

## 1) Run baseline (without OTel)

```bash
mkdir -p runs
LOCUST_RUN_LABEL=without-otel \
LOCUST_WEIGHT_ANON=7 LOCUST_WEIGHT_AUTH=3 \
LOCUST_TASK_WEIGHT_INDEX=3 LOCUST_TASK_WEIGHT_VIEW_COURSE=2 LOCUST_TASK_WEIGHT_TOGGLE_BLOCK=1 \
locust -f locustfile.py --headless -u 100 -r 10 -t 10m --csv runs/without_otel
```

## 2) Run with OTel enabled

```bash
LOCUST_RUN_LABEL=with-otel \
LOCUST_WEIGHT_ANON=7 LOCUST_WEIGHT_AUTH=3 \
LOCUST_TASK_WEIGHT_INDEX=3 LOCUST_TASK_WEIGHT_VIEW_COURSE=2 LOCUST_TASK_WEIGHT_TOGGLE_BLOCK=1 \
locust -f locustfile.py --headless -u 100 -r 10 -t 10m --csv runs/with_otel
```

## 3) Compare both runs

```bash
python3 compare_locust_runs.py \
  --baseline runs/without_otel_stats.csv \
  --otel runs/with_otel_stats.csv \
  --top 10
```

The comparator reports global and per-endpoint deltas for:
- requests
- failures/failure rate
- avg, p50, p95, p99 latency

Interpretation rule of thumb:
- Lower latency and failure rate is better.
- Higher requests at same user load can indicate lower overhead.

## 4) Suggested practice

- Repeat each scenario 3-5 times and compare medians, not single runs.
- Keep load, user mix, task weights, duration, and test environment identical between A/B runs.
- Include a 1-2 minute warm-up (part of total duration) before trusting steady-state numbers.

## 5) Docker/distributed notes

- `compose.yaml` sets `LOCUST_WORKER_INDEX` and `LOCUST_WORKER_COUNT` per worker so each worker uses a shard of `userlist.csv`.
- In `compose.yaml`, `master` uses `--expect-workers 5`; keep this value equal to the number of worker services.
- Cache warmup (`LOCUST_WARM_CACHE=1`) runs once on master/local only; workers do not run warmup.
- Custom metrics are merged from workers into master via Locust's worker report channel, so the final summary is cluster-wide.
