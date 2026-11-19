# Silver: preparation, cleaning and standardization

## Job task 1, `prepare_sources`

- [`prepare_checks_jsonl.ipynb`](prepare_checks_jsonl.ipynb) streams each original JSON
  array into bounded JSON Lines shards (~16 MiB). It preserves business tokens and adds
  `_source_file` lineage. SHA256 manifests let unchanged sources be reused, and the
  active inventory is published last.
- [`prepare_checks_jsonl_source.py`](prepare_checks_jsonl_source.py) holds the same logic as
  an importable module, tested by [`tests/test_jsonl_preparation.py`](../../../tests/test_jsonl_preparation.py).

## Pipeline library

[`mv_checks_cleaned.py`](mv_checks_cleaned.py) declares nine materialized views:

- source checks;
- location and channel references;
- assessed checks;
- accepted checks (liquid clustered by `business_date`, `LocationId`);
- quarantine;
- valid out-of-scope checks;
- discount events;
- payments.

Expectations warn on diagnostic rules and fail on reference uniqueness and on the
validity of published checks. Dataset definitions return DataFrames without
write or collect actions.

These files stay in this folder because the live Databricks job and pipeline
reference these exact paths.
