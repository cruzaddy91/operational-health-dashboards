# Architecture

```
+-----------------------+        scrape         +--------------+
|   Python emitter      |  <----------------+   |  Prometheus  |
|   (src/emitter.py)    |  exposes /metrics |   |  + alert     |
|   port 9100           |                       |  rules       |
+-----------------------+                       +------+-------+
                                                       |
                                                       | datasource
                                                       v
                                                +--------------+
                                                |   Grafana    |
                                                |  Portfolio   |
                                                |  Health dash |
                                                |  port 3000   |
                                                +--------------+
```

## Components

- **emitter** — A Python process that simulates a portfolio of services and exposes Prometheus-format metrics. Includes a small fault injector so alerts fire during the demo.
- **Prometheus** — Scrapes the emitter every 5 seconds. Evaluates three alert rules (error rate, p95 latency, freshness lag).
- **Grafana** — Pre-provisioned with the Prometheus datasource and the Portfolio Health dashboard.

## Why these choices

- **Emitter pretends to be the services**, not a fake monitoring agent. That keeps the Prometheus side realistic.
- **All config is in version control**, including the dashboard JSON. The point is to demonstrate "dashboards as code," not "click around in the UI."
- **Bounded synthetic data with a seeded RNG** so two runs produce comparable shapes for screenshots and demos.

## Adapting to a real portfolio

Replace the emitter with one or more of:

- `node-exporter` for host metrics
- `blackbox-exporter` for vendor endpoint reachability
- A small custom exporter that wraps a vendor's status API
- Application-level instrumentation in your own services

The Prometheus + alert rules + Grafana provisioning pattern stays identical.
