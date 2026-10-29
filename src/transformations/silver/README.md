# Silver: cleaned and standardized source logic

Active pipeline library: `mv_checks_cleaned.py`.

Run `prepare_checks_jsonl.ipynb` as a separate notebook before refreshing the
pipeline. Its source counterpart is `prepare_checks_jsonl_source.py` (distinct
base name for Databricks Git compatibility). It streams original arrays into
bounded JSONL shards, preserves business tokens and lineage, and verifies SHA256
caches. The job automates this as its first task. Do not include preparation
or historical notebooks in the pipeline library list.

It declares nine datasets: source checks, location/channel references, assessed
checks, accepted checks, quarantine, valid out-of-scope checks, discount events
and payments. Dataset definitions return DataFrames without write/collect actions.
The parent pipeline and task orchestration live under `resources/`.

Files beginning with `historical_` retain the Week 4 setup/source helpers. They
are excluded from the Lakeflow library list. Current execution instructions are
in the repository root and Gold runbook.
