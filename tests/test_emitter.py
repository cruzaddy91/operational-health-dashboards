"""Smoke tests for the synthetic portfolio emitter."""

import random

from src.emitter import (
    PORTFOLIO,
    REGISTRY,
    emit_api_tick,
    emit_pipeline_tick,
    update_freshness,
    maybe_inject_fault,
)


def test_portfolio_has_expected_services():
    names = {s.name for s in PORTFOLIO}
    assert {"bc_connector", "partner_api", "reporting_endpoint"} <= names
    assert any(s.is_pipeline for s in PORTFOLIO)


def test_emit_api_tick_does_not_raise():
    rng = random.Random(0)
    svc = next(s for s in PORTFOLIO if not s.is_pipeline)
    emit_api_tick(rng, svc, fault={})


def test_emit_pipeline_tick_does_not_raise():
    rng = random.Random(0)
    svc = next(s for s in PORTFOLIO if s.is_pipeline)
    emit_pipeline_tick(rng, svc)


def test_freshness_updates_for_all_services():
    rng = random.Random(0)
    update_freshness(rng, tick=10)
    metric_names = {m.name for m in REGISTRY.collect()}
    assert "portfolio_freshness_lag_seconds" in metric_names


def test_fault_injector_returns_dict():
    rng = random.Random(0)
    fault = maybe_inject_fault(rng, tick=0)
    assert isinstance(fault, dict)
