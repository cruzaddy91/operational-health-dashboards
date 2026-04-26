# operational-health-dashboards

A runnable reference for building health-visibility dashboards over a portfolio of SaaS and vendor systems you do not fully control. Synthetic data, Prometheus and Grafana, one command to start.

## Overview

Most production reliability work happens on stacks where you cannot install a sidecar, edit the source, or trust the vendor's status page. The job is to build *meaningful signals from the outside* and put them somewhere a human can read at 3 AM.

This repository is that pattern, in miniature:

- A small Python emitter pretends to be a portfolio of vendor-managed and in-house services. It produces realistic operational metrics: pipeline run results, end-to-end latency, vendor API health, freshness lag, and error rates.
- Prometheus scrapes the emitter and evaluates a small set of alert rules.
- Grafana ships pre-provisioned with a portfolio-health dashboard so the demo is one command and zero clicks to a working view.

The whole stack runs locally in Docker. No cloud account, no vendor credentials, no proprietary code.

## Why This Exists

This is the operational pattern I run at work, generalized and made shareable. In a real role I am responsible for the health of a portfolio that includes systems I do not own (Business Central, vendor connectors, partner reporting contracts). I cannot wait for those vendors to expose the right signal; I have to design my own from the outside, route it to a place humans look, and write the alert rule that pages someone.

This repo demonstrates the workflow end to end so a reviewer can clone it, run `make demo`, and see the same shape of work in five minutes.

## Tech Stack

- Python 3.12, prometheus-client
- Prometheus (latest)
- Grafana (latest, pre-provisioned datasource and dashboard)
- Docker, Docker Compose
- pytest

## Quick Start

Requires Docker Desktop (or any Docker engine) and `make`.

```bash
git clone https://github.com/cruzaddy91/operational-health-dashboards.git
cd operational-health-dashboards

make demo
```

Then open:

- Grafana: http://localhost:3000 (admin / admin) and the **Portfolio Health** dashboard is pre-provisioned.
- Prometheus: http://localhost:9090 and the alerts tab shows fired/pending alerts.
- Emitter raw metrics: http://localhost:9100/metrics

Stop everything:

```bash
make down
```

## What You Are Looking At

The emitter simulates a small portfolio of services to make the dashboard non-empty:

| Service | Type | What it emits |
|---|---|---|
| `bc_connector` | vendor SaaS (Business Central style) | API success rate, latency p95, freshness lag |
| `etl_pipeline_finance` | in-house pipeline | run result, duration, rows processed |
| `etl_pipeline_sales` | in-house pipeline | run result, duration, rows processed |
| `reporting_endpoint` | downstream consumer | refresh status, lag-vs-source |
| `partner_api` | external vendor | success rate, latency p95, 5xx rate |

A small fault injector occasionally degrades one of the services so the alert rules and dashboard panels actually fire.

The dashboard groups the panels by the question they answer, not by the metric name. That is intentional: the panels you watch at 3 AM should be ordered by *what is on fire*, not by metric taxonomy.

## Repository Structure

```text
operational-health-dashboards/
├── README.md
├── Makefile
├── docker-compose.yml
├── Dockerfile.emitter
├── requirements.txt
├── src/
│   └── emitter.py                # synthetic portfolio + Prometheus exporter
├── prometheus/
│   ├── prometheus.yml            # scrape config
│   └── alerts.yml                # alert rules (latency, error rate, freshness)
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml
│       └── dashboards/
│           ├── dashboards.yml
│           └── portfolio_health.json
├── tests/
│   └── test_emitter.py
└── docs/
    └── architecture.md
```

## Design Notes

A few choices worth being explicit about:

- **The emitter is not a fake monitoring agent.** It pretends to be the *services themselves*, exposing `/metrics` like a real instrumented app. That keeps the Prometheus side of the demo realistic.
- **Alerts are deliberately small.** Three rules, one per failure mode (latency burn, error rate, freshness lag). A real shop has more, but a tutorial buried in alert noise teaches nothing.
- **Dashboards are version-controlled JSON, provisioned at startup.** No "click around in Grafana to set this up." That is the actual operational lesson: dashboards are code.
- **Synthetic data is bounded and reproducible.** The emitter uses a seeded RNG so two runs produce comparable shapes for screenshots and demos.

## Extending

Useful next steps if you want to fork and adapt:

- Point Prometheus at a real exporter (node-exporter, blackbox-exporter against a vendor endpoint, etc.) and watch the same dashboard pattern keep working.
- Add an Alertmanager container and route the alerts to a real notification channel.
- Add a second emitter that simulates a slow rollout (canary degradation) and a panel that shows the canary-vs-baseline comparison.

## License

MIT. See [LICENSE](LICENSE).

## Author

Addy Cruz. [Portfolio](https://addycportfolio.netlify.app), [LinkedIn](https://www.linkedin.com/in/cruzadam91)
