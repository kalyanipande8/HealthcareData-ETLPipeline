"""Real SLA compliance check: the ETL pipeline's actual measured runtime
against a defined processing-time SLA for the 340K-record volume."""
from __future__ import annotations

SLA_SECONDS = 60.0  # target: process the full batch within 60 seconds


def check_sla_compliance(elapsed_sec: float, sla_seconds: float = SLA_SECONDS) -> dict:
    return {
        "elapsed_sec": round(elapsed_sec, 3),
        "sla_seconds": sla_seconds,
        "within_sla": elapsed_sec <= sla_seconds,
        "sla_margin_pct": round(100 * (sla_seconds - elapsed_sec) / sla_seconds, 2),
    }


if __name__ == "__main__":
    from .simulate_raw_claims import simulate
    from .etl_pipeline import run_etl

    raw = simulate()
    result = run_etl(raw)
    print(check_sla_compliance(result["elapsed_sec"]))
