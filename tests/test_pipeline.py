import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_raw_claims import simulate
from src.etl_pipeline import run_etl
from src.quality_checks import run_quality_checks, overall_accuracy
from src.sla_compliance import check_sla_compliance


@pytest.fixture(scope="module")
def raw():
    return simulate(n=20_000, seed=157)  # smaller subset for fast test iteration


@pytest.fixture(scope="module")
def etl_result(raw):
    return run_etl(raw, out_path="data/test_output.csv")


def test_simulation_produces_expected_scale():
    full = simulate()
    assert len(full) >= 340_000


def test_etl_deduplicates_claim_ids(etl_result):
    assert not etl_result["transformed"]["claim_id"].duplicated().any()


def test_etl_removes_all_missing_claim_amounts(etl_result):
    assert etl_result["transformed"]["claim_amount"].notna().all()


def test_etl_normalizes_unknown_status(etl_result):
    assert "Unknown" not in etl_result["transformed"]["claim_status"].unique()


def test_exactly_45_quality_checks_run(etl_result):
    checks = run_quality_checks(etl_result["transformed"])
    assert len(checks) == 45


def test_overall_quality_accuracy_in_realistic_band(etl_result):
    checks = run_quality_checks(etl_result["transformed"])
    accuracy = overall_accuracy(checks)
    assert 90.0 <= accuracy["overall_accuracy_pct"] <= 100.0


def test_sla_compliance_check_runs(etl_result):
    sla = check_sla_compliance(etl_result["elapsed_sec"])
    assert sla["within_sla"] is True
