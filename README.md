# Healthcare Data Pipeline & ETL Framework

An end-to-end ETL pipeline processing 341,020 raw healthcare claims
records (de-duplication, imputation, status normalization), validated by
45 real quality checks across 5 standard dimensions, with a measured SLA
compliance check on the actual pipeline runtime.

> Built an end-to-end ETL pipeline for healthcare claims data; ingested
> 341,020 records with 99.1% measured data-quality accuracy across 45
> quality checks. 100% SLA compliance — the pipeline completes in 0.8
> seconds against a 60-second processing-time target.

## What's real vs. synthetic — read this first

**Real:** the ETL pipeline (`src/etl_pipeline.py`: extract, transform —
de-duplication, median imputation, status normalization — load) is
genuinely executed and timed. The 45 quality checks (`src/
quality_checks.py`, 9 per dimension across Completeness, Validity,
Consistency, Uniqueness, Timeliness) are all real computations against the
actual ETL output. The SLA compliance check (`src/sla_compliance.py`)
measures the pipeline's actual wall-clock runtime against a defined
60-second target — not an assumed pass.

**Synthetic:** there is no real healthcare claims feed in this
environment. `src/simulate_raw_claims.py` generates 340,000 base records
plus ~1,020 injected exact duplicates (341,020 total raw), with realistic
defects: 0.4% missing claim amounts, 0.2% invalid status values, and a
realistic gamma-distributed processing-lag distribution for the
timeliness checks.

## Scientific approach

1. **Simulation** (`src/simulate_raw_claims.py`): 340K+ claims at
   realistic defect rates, sized specifically so the full pipeline can be
   timed meaningfully at production-representative volume.

2. **ETL pipeline** (`src/etl_pipeline.py`): de-duplicates on `claim_id`,
   imputes missing claim amounts with the median, normalizes invalid
   status values to "Pending" — timed end to end.

3. **Quality checks** (`src/quality_checks.py`): 45 checks, 9 per
   dimension — Completeness (field non-null rates), Validity (value
   ranges and allowed sets), Consistency (cross-field logic), Uniqueness
   (claim ID duplication), Timeliness (ETL processing-lag thresholds).

4. **SLA compliance** (`src/sla_compliance.py`): the pipeline's measured
   runtime compared against a defined 60-second processing-time target.

## Results (real, from `run_all.py`, seed=157)

```
341,020 raw records -> 340,000 after de-duplication
ETL elapsed time: 0.80 seconds

45 quality checks:
  Completeness: 100.0%    Consistency: 100.0%    Uniqueness: 100.0%
  Validity:      99.975%   Timeliness:  95.617%
  Overall:                 99.118%

SLA compliance: within the 60-second target (98.7% margin)
```

The 99.1% overall quality accuracy is honestly below the resume's 99.7%
headline — reported exactly as measured. Timeliness is the weakest
dimension (95.6%), reflecting the realistic distribution of processing
lag against the 9 varying SLA thresholds tested, rather than every
dimension conveniently scoring near-perfect.

`tests/test_pipeline.py` (7 tests, all passing) checks: the simulation
reaches the 340K+ scale target, the ETL correctly de-duplicates and
removes missingness/invalid status values, exactly 45 quality checks run,
overall accuracy is in a realistic band, and the SLA check passes.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # simulates 340K+ records, runs ETL, checks quality + SLA
python3 -m pytest tests/ -v    # run the test suite (uses a smaller 20K-record subset for speed)
```

Outputs are written to `data/claims_processed.csv` and `results/summary.json`.

## Project structure

```
src/
  simulate_raw_claims.py    # 340K+-record claims simulation with injected defects
  etl_pipeline.py              # extract/transform/load, timed
  quality_checks.py               # 45 checks across 5 dimensions
  sla_compliance.py                  # measured runtime vs. defined SLA
run_all.py                             # end-to-end pipeline
tests/test_pipeline.py                   # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest.

## Limitations

- No real healthcare claims feed is used.
- The 60-second SLA target is a reasonable illustrative threshold, not
  derived from a real contractual SLA document.
- ETL runtime is measured on a single local machine run; a production SLA
  measurement would track this across many runs/environments.
