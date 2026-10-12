"""Simulate 340,000 raw healthcare claims records with realistic injected
defects -- the scale target named in the resume bullet, generated
efficiently with vectorized numpy so the full ETL pipeline actually runs
end to end at this volume."""
from __future__ import annotations

import numpy as np
import pandas as pd

N_RECORDS = 340_000
SEED = 157


def simulate(n: int = N_RECORDS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    df = pd.DataFrame({
        "claim_id": np.arange(n),
        "beneficiary_id": rng.integers(0, 60_000, n),
        "claim_amount": np.round(rng.gamma(2, 120, n), 2),
        "claim_status": rng.choice(["Paid", "Denied", "Pending"], n, p=[0.75, 0.15, 0.10]),
        "service_date_offset": rng.integers(0, 365, n),
        "processing_lag_days": rng.gamma(2, 3, n).round(1),  # days between service and ETL ingestion
    })

    # realistic injected defects at ETL-relevant rates
    missing_idx = rng.choice(df.index, size=int(n * 0.004), replace=False)
    df.loc[missing_idx, "claim_amount"] = np.nan

    bad_status_idx = rng.choice(df.index, size=int(n * 0.002), replace=False)
    df.loc[bad_status_idx, "claim_status"] = "Unknown"

    dup_idx = rng.choice(df.index, size=int(n * 0.003), replace=False)
    dupes = df.loc[dup_idx].copy()
    df = pd.concat([df, dupes], ignore_index=True)

    return df


if __name__ == "__main__":
    df = simulate()
    print(df.shape)
