import itertools
import os
import threading
import time
import urllib.request
from collections import defaultdict

from locust import HttpUser, LoadTestShape, between, events, task
from locust.runners import LocalRunner, MasterRunner, WorkerRunner
from pyquery import PyQuery
import csv


USERS_FILE = os.path.join(os.path.dirname(__file__), "userlist.csv")
COURSE_SHORTNAME = int(os.getenv("LOCUST_COURSE_SHORTNAME", "14"))
WAIT_TIME_SECONDS_MIN = float(os.getenv("LOCUST_WAIT_MIN", "1"))
WAIT_TIME_SECONDS_MAX = float(os.getenv("LOCUST_WAIT_MAX", "5"))
VERBOSE = os.getenv("LOCUST_VERBOSE", "0") == "1"
RUN_LABEL = os.getenv("LOCUST_RUN_LABEL", "baseline")
ANON_USER_WEIGHT = int(os.getenv("LOCUST_WEIGHT_ANON", "1"))
AUTH_USER_WEIGHT = int(os.getenv("LOCUST_WEIGHT_AUTH", "1"))

TASK_WEIGHT_INDEX = int(os.getenv("LOCUST_TASK_WEIGHT_INDEX", "3"))
TASK_WEIGHT_VIEW_COURSE = int(os.getenv("LOCUST_TASK_WEIGHT_VIEW_COURSE", "2"))
TASK_WEIGHT_TOGGLE_BLOCK = int(os.getenv("LOCUST_TASK_WEIGHT_TOGGLE_BLOCK", "1"))
TASK_WEIGHT_FETCH_AMD = int(os.getenv("LOCUST_TASK_WEIGHT_FETCH_AMD", "1"))
TASK_WEIGHT_FETCH_YUI = int(os.getenv("LOCUST_TASK_WEIGHT_FETCH_YUI", "4"))
TASK_WEIGHT_FETCH_ESM = int(os.getenv("LOCUST_TASK_WEIGHT_FETCH_ESM", "4"))
TASK_WEIGHT_FETCH_CSS = int(os.getenv("LOCUST_TASK_WEIGHT_FETCH_CSS", "1"))
TASK_WEIGHT_FETCH_YUI_CSS = int(os.getenv("LOCUST_TASK_WEIGHT_FETCH_YUI_CSS", "1"))
WARM_CACHE_ENABLED = os.getenv("LOCUST_WARM_CACHE", "1") == "1"
WARM_CACHE_REPEATS = int(os.getenv("LOCUST_WARM_CACHE_REPEATS", "1"))
WARM_CACHE_TIMEOUT_SECONDS = int(os.getenv("LOCUST_WARM_CACHE_TIMEOUT", "10"))
STATIC_BASE_URL = os.getenv("LOCUST_STATIC_BASE_URL").rstrip("/")
WORKER_INDEX = int(os.getenv("LOCUST_WORKER_INDEX", "-1"))
WORKER_COUNT = int(os.getenv("LOCUST_WORKER_COUNT", "0"))
ASSET_DEFAULT_AGE_SECONDS = int(os.getenv("LOCUST_ASSET_DEFAULT_AGE_SECONDS", "300"))
ASSET_MAX_AGE_SECONDS = int(os.getenv("LOCUST_ASSET_MAX_AGE_SECONDS", "86400"))
ENABLE_LOAD_SHAPE = os.getenv("LOCUST_ENABLE_LOAD_SHAPE", "1") == "1"

SHAPE_WARMUP_DURATION = int(os.getenv("LOCUST_SHAPE_WARMUP_DURATION", "120"))
SHAPE_WARMUP_USERS = int(os.getenv("LOCUST_SHAPE_WARMUP_USERS", "20"))
SHAPE_WARMUP_SPAWN = float(os.getenv("LOCUST_SHAPE_WARMUP_SPAWN", "5"))

SHAPE_STEADY_DURATION = int(os.getenv("LOCUST_SHAPE_STEADY_DURATION", "600"))
SHAPE_STEADY_USERS = int(os.getenv("LOCUST_SHAPE_STEADY_USERS", "80"))
SHAPE_STEADY_SPAWN = float(os.getenv("LOCUST_SHAPE_STEADY_SPAWN", "10"))

SHAPE_RAMPDOWN_DURATION = int(os.getenv("LOCUST_SHAPE_RAMPDOWN_DURATION", "60"))
SHAPE_RAMPDOWN_USERS = int(os.getenv("LOCUST_SHAPE_RAMPDOWN_USERS", "0"))
SHAPE_RAMPDOWN_SPAWN = float(os.getenv("LOCUST_SHAPE_RAMPDOWN_SPAWN", "20"))


def resolve_asset_version():
    now = int(time.time())
    source = "env"

    value = now - max(ASSET_DEFAULT_AGE_SECONDS, 1)
    source = "auto"

    if value >= now:
        value = now - 1

    age = now - value
    if age > ASSET_MAX_AGE_SECONDS:
        print(
            f"[bench] warning asset_version age={age}s exceeds "
            f"ASSET_MAX_AGE_SECONDS={ASSET_MAX_AGE_SECONDS}"
        )

    return str(value), source


ASSET_VERSION, ASSET_VERSION_SOURCE = resolve_asset_version()

YUI_URL = f"{STATIC_BASE_URL}/theme/yui_combo.php?rollup/3.18.1/yui-moodlesimple.js"
AMD_URL = f"{STATIC_BASE_URL}/lib/requirejs.php/{ASSET_VERSION}/core/first.js"
ESM_URL = f"{STATIC_BASE_URL}/r.php/core/esm/{ASSET_VERSION}/react"
CSS_URL = f"{STATIC_BASE_URL}/theme/styles.php/boost/{ASSET_VERSION}_{ASSET_VERSION}/all"
YUI_CSS_URL = f"{STATIC_BASE_URL}/theme/yui_combo.php?rollup/3.18.1/yui-moodlesimple.css"


def warm_static_cache():
    warm_urls = [YUI_URL, AMD_URL, ESM_URL, CSS_URL, YUI_CSS_URL]
    total_attempts = len(warm_urls) * max(WARM_CACHE_REPEATS, 0)
    success_count = 0

    if total_attempts == 0:
        print("[bench] warm-cache skipped because repeat count is 0")
        return

    print(f"[bench] warm-cache starting repeats={WARM_CACHE_REPEATS} urls={len(warm_urls)}")

    for _ in range(WARM_CACHE_REPEATS):
        for url in warm_urls:
            request = urllib.request.Request(url, headers={"User-Agent": "locust-cache-warmer/1.0"})
            try:
                with urllib.request.urlopen(request, timeout=WARM_CACHE_TIMEOUT_SECONDS) as response:
                    if 200 <= response.status < 400:
                        success_count += 1
            except Exception as error:
                if VERBOSE:
                    print(f"[bench] warm-cache failed url={url} error={error}")

    print(f"[bench] warm-cache complete success={success_count}/{total_attempts}")

def load_users(path):
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader if len(row) >= 2]


def shard_users(all_users):
    if WORKER_COUNT <= 0 or WORKER_INDEX < 0:
        return all_users

    shard = all_users[WORKER_INDEX::WORKER_COUNT]
    if not shard:
        raise RuntimeError(
            f"No users assigned for shard index={WORKER_INDEX} count={WORKER_COUNT}. "
            "Check LOCUST_WORKER_INDEX/LOCUST_WORKER_COUNT or increase userlist.csv"
        )
    return shard


users = shard_users(load_users(USERS_FILE))
if not users:
    raise RuntimeError("No users found in userlist.csv")

user_cycle = itertools.cycle(users)
user_cycle_lock = threading.Lock()


class CustomMetrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.aggregates = defaultdict(lambda: {
            "count": 0,
            "sum": 0.0,
            "min": None,
            "max": None,
        })
        self.counters = defaultdict(int)

    def record_value(self, name, value):
        value = float(value)
        with self.lock:
            aggregate = self.aggregates[name]
            aggregate["count"] += 1
            aggregate["sum"] += value
            aggregate["min"] = value if aggregate["min"] is None else min(aggregate["min"], value)
            aggregate["max"] = value if aggregate["max"] is None else max(aggregate["max"], value)

    def increment(self, name, amount=1):
        with self.lock:
            self.counters[name] += amount

    def get_value_stats(self, name):
        with self.lock:
            aggregate = self.aggregates.get(name)
            if not aggregate or aggregate["count"] == 0:
                return None
            return {
                "count": aggregate["count"],
                "min": aggregate["min"],
                "max": aggregate["max"],
                "avg": aggregate["sum"] / aggregate["count"],
            }

    def snapshot(self):
        with self.lock:
            return {
                "counters": dict(self.counters),
                "aggregates": {name: dict(value) for name, value in self.aggregates.items()},
            }

    def merge_snapshot(self, snapshot):
        if not snapshot:
            return

        with self.lock:
            for key, value in snapshot.get("counters", {}).items():
                self.counters[key] += int(value)

            for name, value in snapshot.get("aggregates", {}).items():
                incoming_count = int(value.get("count", 0))
                if incoming_count == 0:
                    continue

                incoming_sum = float(value.get("sum", 0.0))
                incoming_min = value.get("min")
                incoming_max = value.get("max")

                target = self.aggregates[name]
                target["count"] += incoming_count
                target["sum"] += incoming_sum

                if incoming_min is not None:
                    target["min"] = incoming_min if target["min"] is None else min(target["min"], incoming_min)
                if incoming_max is not None:
                    target["max"] = incoming_max if target["max"] is None else max(target["max"], incoming_max)


custom_metrics = CustomMetrics()
run_start_time = None


def is_worker(environment):
    return isinstance(environment.runner, WorkerRunner)


def is_master(environment):
    return isinstance(environment.runner, MasterRunner)


def is_local(environment):
    return isinstance(environment.runner, LocalRunner)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global run_start_time

    if WARM_CACHE_ENABLED:
        warm_static_cache()

    run_start_time = time.time()
    print(
        f"[bench] run_label={RUN_LABEL} users_loaded={len(users)} "
        f"wait={WAIT_TIME_SECONDS_MIN}-{WAIT_TIME_SECONDS_MAX}s COURSE_SHORTNAME={COURSE_SHORTNAME} "
        f"weight_anon={ANON_USER_WEIGHT} weight_auth={AUTH_USER_WEIGHT} "
        f"warm_cache={WARM_CACHE_ENABLED} worker_index={WORKER_INDEX} worker_count={WORKER_COUNT} "
        f"asset_version={ASSET_VERSION} asset_version_source={ASSET_VERSION_SOURCE}"
    )


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, exception, **kwargs):
    custom_metrics.record_value("response_time_ms", response_time)
    custom_metrics.record_value("response_length_bytes", response_length)

    if exception is not None:
        custom_metrics.increment("request_exceptions")

    if response is not None:
        custom_metrics.increment(f"status_{response.status_code}")

        memory_total = response.headers.get("x-memory-total")
        if memory_total is not None:
            try:
                custom_metrics.record_value("memory_total_mb", memory_total)
            except ValueError:
                custom_metrics.increment("invalid_x_memory_total")

        memory_growth = response.headers.get("x-memory-growth")
        if memory_growth is not None:
            try:
                custom_metrics.record_value("memory_growth_mb", memory_growth)
            except ValueError:
                custom_metrics.increment("invalid_x_memory_growth")

        content_type = response.headers.get("content-type", "unknown").split(";")[0].strip()
        custom_metrics.increment(f"content_type::{content_type}")

    if VERBOSE:
        print(
            f"[req] {request_type} {name} time={response_time:.1f}ms "
            f"bytes={response_length} exception={exception is not None}"
        )


def _print_value_metric(name, unit=""):
    stats = custom_metrics.get_value_stats(name)
    if not stats:
        print(f"  {name}: n/a")
        return
    suffix = f"{unit}" if unit else ""
    print(
        f"  {name}: count={stats['count']} min={stats['min']:.2f}{suffix} "
        f"max={stats['max']:.2f}{suffix} avg={stats['avg']:.2f}{suffix}"
    )


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    if is_worker(environment):
        return

    run_duration = (time.time() - run_start_time) if run_start_time else 0
    total_stats = environment.stats.total

    print("\n=== Benchmark Summary ===")
    print(f"run_label: {RUN_LABEL}")
    print(f"duration_s: {run_duration:.1f}")
    print(f"requests: {total_stats.num_requests}")
    print(f"failures: {total_stats.num_failures}")
    print(f"rps_current: {total_stats.current_rps:.2f}")
    print(f"rps_total: {total_stats.total_rps:.2f}")
    print(f"latency_p50_ms: {total_stats.get_response_time_percentile(0.50):.2f}")
    print(f"latency_p95_ms: {total_stats.get_response_time_percentile(0.95):.2f}")
    print(f"latency_p99_ms: {total_stats.get_response_time_percentile(0.99):.2f}")

    print("custom_values:")
    _print_value_metric("response_time_ms", "ms")
    _print_value_metric("response_length_bytes", "B")
    _print_value_metric("memory_total_mb", "MB")
    _print_value_metric("memory_growth_mb", "MB")

    print("custom_counters:")
    for key, value in sorted(custom_metrics.snapshot().get("counters", {}).items()):
        print(f"  {key}={value}")


@events.report_to_master.add_listener
def on_report_to_master(client_id, data):
    data["custom_metrics"] = custom_metrics.snapshot()


@events.worker_report.add_listener
def on_worker_report(client_id, data):
    custom_metrics.merge_snapshot(data.get("custom_metrics"))


print(
    f"Loaded {len(users)} users from userlist.csv "
    f"(shard index={WORKER_INDEX}, shard count={WORKER_COUNT})"
)


class MoodleBaseUser(HttpUser):
    abstract = True
    wait_time = between(WAIT_TIME_SECONDS_MIN, WAIT_TIME_SECONDS_MAX)

    def loginAsNextUser(self):
        with user_cycle_lock:
            username, password = next(user_cycle)

        return self.loginAs(username, password)

    def loginAs(self, username, password):
        r = self.client.get('/login/index.php')

        # Parse the login page to extract the logintoken
        d = PyQuery(r.text)
        logintoken = d('input[name=logintoken]').val()
        r = self.client.post('/login/index.php', {
            "username": username,
            "password": password,
            "logintoken": logintoken,
        });

        if r.status_code != 200:
            print(f"Login failed for user {username} with status code {r.status_code}")
            custom_metrics.increment("login_failures")
        else:
            custom_metrics.increment("login_success")

        return r


class AnonymousMoodleUser(MoodleBaseUser):
    weight = ANON_USER_WEIGHT

    @task(TASK_WEIGHT_INDEX)
    def index_page(self):
        r = self.client.get("/", name="anon:index")
        if r.status_code != 200:
            print(f"Failed to load anon index page with status code {r.status_code}")

    @task(TASK_WEIGHT_VIEW_COURSE)
    def view_course_anonymous(self):
        r = self.client.get(f'/course/view.php?name={COURSE_SHORTNAME}', name="anon:view_course")
        if VERBOSE:
            print(f"Anonymous view course returned status code {r.status_code}")

    @task(TASK_WEIGHT_FETCH_YUI)
    def fetch_yui(self):
        print(f"Fetching YUI combo from {YUI_URL}")
        r = self.client.get(YUI_URL, name="anon:fetch_yui")
        if r.status_code != 200:
            print(f"Failed to fetch YUI combo with status code {r.status_code}")

    @task(TASK_WEIGHT_FETCH_AMD)
    def fetch_amd(self):
        print(f"Fetching AMD combo from {AMD_URL}")
        r = self.client.get(AMD_URL, name="anon:fetch_amd")
        if r.status_code != 200:
            print(f"Failed to fetch AMD combo with status code {r.status_code}")

    @task(TASK_WEIGHT_FETCH_ESM)
    def fetch_esm(self):
        print(f"Fetching ESM combo from {ESM_URL}")
        r = self.client.get(ESM_URL, name="anon:fetch_esm")
        if r.status_code != 200:
            print(f"Failed to fetch ESM combo with status code {r.status_code}")

    @task(TASK_WEIGHT_FETCH_CSS)
    def fetch_css(self):
        r = self.client.get(CSS_URL, name="anon:fetch_css")
        if r.status_code != 200:
            print(f"Failed to fetch CSS combo with status code {r.status_code}")

    @task(TASK_WEIGHT_FETCH_YUI_CSS)
    def fetch_yui_css(self):
        r = self.client.get(YUI_CSS_URL, name="anon:fetch_yui_css")
        if r.status_code != 200:
            print(f"Failed to fetch YUI CSS combo with status code {r.status_code}")

class AuthenticatedMoodleUser(MoodleBaseUser):
    weight = AUTH_USER_WEIGHT

    def on_start(self):
        self.wait()
        self.loginAsNextUser()

    @task(TASK_WEIGHT_INDEX)
    def index_page(self):
        r = self.client.get("/", name="auth:index")
        if r.status_code != 200:
            print(f"Failed to load auth index page with status code {r.status_code}")

    @task(TASK_WEIGHT_TOGGLE_BLOCK)
    def toggleBlock(self):
        self.client.post(
            '/api/rest/v2/user/current/preferences/drawer-open-block',
            json={"value": True},
            name="auth:toggle_block_on"
        )
        self.client.post(
            '/api/rest/v2/user/current/preferences/drawer-open-block',
            json={"value": False},
            name="auth:toggle_block_off"
        )

    @task(TASK_WEIGHT_VIEW_COURSE)
    def viewCourse(self):
        r = self.client.get(f'/course/view.php?name={COURSE_SHORTNAME}', name="auth:view_course")
        if VERBOSE:
            print(f"Authenticated view course returned status code {r.status_code}")


if ENABLE_LOAD_SHAPE:
    class ReproducibleBenchmarkShape(LoadTestShape):
        stages = [
            {
                "duration": SHAPE_WARMUP_DURATION,
                "users": SHAPE_WARMUP_USERS,
                "spawn_rate": SHAPE_WARMUP_SPAWN,
            },
            {
                "duration": SHAPE_WARMUP_DURATION + SHAPE_STEADY_DURATION,
                "users": SHAPE_STEADY_USERS,
                "spawn_rate": SHAPE_STEADY_SPAWN,
            },
            {
                "duration": SHAPE_WARMUP_DURATION + SHAPE_STEADY_DURATION + SHAPE_RAMPDOWN_DURATION,
                "users": SHAPE_RAMPDOWN_USERS,
                "spawn_rate": SHAPE_RAMPDOWN_SPAWN,
            },
        ]

        def tick(self):
            run_time = self.get_run_time()
            for stage in self.stages:
                if run_time < stage["duration"]:
                    return (stage["users"], stage["spawn_rate"])
            return None
