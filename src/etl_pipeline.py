"""Real extract-transform-load pipeline: de-duplication, missing-value
imputation, and status normalization, timed end to end for the SLA
compliance check."""
from __future__ import annotations

import time

import pandas as pd


def extract(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()


def transform(df: pd.DataFrame) -> pd.DataFrame:
    out = df.drop_duplicates(subset=["claim_id"], keep="first").copy()
    out["claim_amount"] = out["claim_amount"].fillna(out["claim_amount"].median())
    out["claim_status"] = out["claim_status"].replace("Unknown", "Pending")
    return out


def load(df: pd.DataFrame, out_path: str) -> None:
    df.to_csv(out_path, index=False)


def run_etl(raw: pd.DataFrame, out_path: str = "data/claims_processed.csv") -> dict:
    start = time.perf_counter()
    extracted = extract(raw)
    transformed = transform(extracted)
    load(transformed, out_path)
    elapsed = time.perf_counter() - start

    return {"n_input_records": len(raw), "n_output_records": len(transformed), "elapsed_sec": round(elapsed, 3),
            "transformed": transformed}


if __name__ == "__main__":
    from .simulate_raw_claims import simulate

    raw = simulate()
    result = run_etl(raw)
    print({k: v for k, v in result.items() if k != "transformed"})
