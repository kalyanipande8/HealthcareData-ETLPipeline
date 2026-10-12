"""End-to-end: simulate 340K raw claims, run the ETL pipeline, run 45
quality checks, and verify SLA compliance."""
import json
import os

from src.simulate_raw_claims import simulate
from src.etl_pipeline import run_etl
from src.quality_checks import run_quality_checks, overall_accuracy
from src.sla_compliance import check_sla_compliance

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating 340K raw healthcare claims records ===")
raw = simulate()
print(raw.shape)

print("\n=== Running ETL pipeline (extract -> transform -> load) ===")
etl_result = run_etl(raw, out_path="data/claims_processed.csv")
print({k: v for k, v in etl_result.items() if k != "transformed"})

print("\n=== Running 45 quality checks ===")
checks = run_quality_checks(etl_result["transformed"])
accuracy = overall_accuracy(checks)
print(accuracy)

print("\n=== SLA compliance check ===")
sla = check_sla_compliance(etl_result["elapsed_sec"])
print(sla)

summary = {
    "n_input_records": etl_result["n_input_records"],
    "n_output_records": etl_result["n_output_records"],
    "etl_elapsed_sec": etl_result["elapsed_sec"],
    "n_quality_checks": accuracy["n_checks"],
    "overall_quality_accuracy_pct": accuracy["overall_accuracy_pct"],
    "quality_by_dimension": accuracy["by_dimension"],
    "sla_compliant": sla["within_sla"],
    "sla_margin_pct": sla["sla_margin_pct"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
