"""Synthetic SaaS-portfolio metrics emitter.

Pretends to be a small portfolio of vendor and in-house services and exposes
realistic operational metrics on /metrics for Prometheus to scrape.

A small fault injector occasionally degrades one service so alert rules and
dashboard panels have something to react to during the demo.
"""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

REGISTRY = CollectorRegistry()

api_requests_total = Counter(
    "portfolio_api_requests_total",
    "Total API requests handled by a service.",
    ["service", "outcome"],
    registry=REGISTRY,
)

api_latency_seconds = Histogram(
    "portfolio_api_latency_seconds",
    "API request latency in seconds.",
    ["service"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY,
)

pipeline_runs_total = Counter(
    "portfolio_pipeline_runs_total",
    "Pipeline run results.",
    ["pipeline", "outcome"],
    registry=REGISTRY,
)

pipeline_duration_seconds = Histogram(
    "portfolio_pipeline_duration_seconds",
    "Pipeline run duration in seconds.",
    ["pipeline"],
    buckets=(10, 30, 60, 120, 300, 600, 1200),
    registry=REGISTRY,
)

freshness_lag_seconds = Gauge(
    "portfolio_freshness_lag_seconds",
    "Seconds since this service last produced fresh data.",
    ["service"],
    registry=REGISTRY,
)


@dataclass
class ServiceProfile:
    name: str
    base_latency: float
    error_rate: float
    fresh_interval: int
    is_pipeline: bool = False


PORTFOLIO: list[ServiceProfile] = [
    ServiceProfile("bc_connector", base_latency=0.40, error_rate=0.01, fresh_interval=3600),
    ServiceProfile("partner_api", base_latency=0.25, error_rate=0.02, fresh_interval=900),
    ServiceProfile("reporting_endpoint", base_latency=0.10, error_rate=0.005, fresh_interval=600),
    ServiceProfile("etl_pipeline_finance", base_latency=0, error_rate=0.05, fresh_interval=21600, is_pipeline=True),
    ServiceProfile("etl_pipeline_sales", base_latency=0, error_rate=0.03, fresh_interval=10800, is_pipeline=True),
]


def maybe_inject_fault(rng: random.Random, tick: int) -> dict[str, float]:
    """Occasionally degrade one service so alerts fire during the demo.

    Returns a dict of service-name -> latency-multiplier and error-rate-add.
    """
    fault: dict[str, dict[str, float]] = {}
    if tick % 60 < 20:
        victim = rng.choice([s.name for s in PORTFOLIO if not s.is_pipeline])
        fault[victim] = {"latency_mult": 4.0, "error_add": 0.10}
    return fault


def emit_api_tick(rng: random.Random, svc: ServiceProfile, fault: dict) -> None:
    requests = rng.randint(20, 80)
    f = fault.get(svc.name, {})
    latency_mult = f.get("latency_mult", 1.0)
    error_add = f.get("error_add", 0.0)
    effective_error_rate = min(1.0, svc.error_rate + error_add)

    for _ in range(requests):
        latency = max(0.01, rng.gauss(svc.base_latency, svc.base_latency * 0.3)) * latency_mult
        api_latency_seconds.labels(svc.name).observe(latency)
        if rng.random() < effective_error_rate:
            api_requests_total.labels(svc.name, "error").inc()
        else:
            api_requests_total.labels(svc.name, "success").inc()


def emit_pipeline_tick(rng: random.Random, svc: ServiceProfile) -> None:
    if rng.random() > 0.05:
        return
    duration = max(5, rng.gauss(180, 60))
    pipeline_duration_seconds.labels(svc.name).observe(duration)
    if rng.random() < svc.error_rate:
        pipeline_runs_total.labels(svc.name, "failure").inc()
    else:
        pipeline_runs_total.labels(svc.name, "success").inc()


def update_freshness(rng: random.Random, tick: int) -> None:
    for svc in PORTFOLIO:
        base_lag = (tick * 5) % svc.fresh_interval
        jitter = rng.uniform(-30, 30)
        freshness_lag_seconds.labels(svc.name).set(max(0, base_lag + jitter))


def main() -> None:
    port = int(os.environ.get("EMITTER_PORT", "9100"))
    seed = int(os.environ.get("EMITTER_SEED", "42"))
    interval = float(os.environ.get("EMITTER_INTERVAL_SECONDS", "1.0"))

    rng = random.Random(seed)
    start_http_server(port, registry=REGISTRY)
    print(f"emitter listening on :{port} (seed={seed}, interval={interval}s)")

    tick = 0
    while True:
        fault = maybe_inject_fault(rng, tick)
        for svc in PORTFOLIO:
            if svc.is_pipeline:
                emit_pipeline_tick(rng, svc)
            else:
                emit_api_tick(rng, svc, fault)
        update_freshness(rng, tick)
        tick += 1
        time.sleep(interval)


if __name__ == "__main__":
    main()
