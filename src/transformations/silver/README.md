# Silver: cleaned and standardized source logic

Active pipeline library: `mv_checks_cleaned.py`.

It declares nine datasets: source checks, location/channel references, assessed
checks, accepted checks, quarantine, valid out-of-scope checks, discount events
and payments. Dataset definitions return DataFrames without write/collect actions.
The parent pipeline and task orchestration live under `resources/`.

Files beginning with `historical_` retain the Week 4 setup/source helpers. They
are excluded from the Lakeflow library list. Current execution instructions are
in the repository root and Gold runbook.
