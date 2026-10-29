# Gold: metrics, reporting and submission evidence

## Active pipeline libraries

- `mv_executive_kpis.sql`: fourteen analytical datasets.
- `mv_quality_metrics.sql`: four quality datasets.

## Execution and explanation

- `RUNBOOK_ES.md`: step-by-step web deployment, execution and evidence capture.
- `DATA_CONTRACT.md`: grains, formulas, null/sign handling and quality policies.
- `RUBRIC_EVIDENCE.md`: implementation mapped to every rubric criterion and pending runtime evidence.
- `validate_pipeline.ipynb`: importable post-run gate, paired with its `.py` source.
- `demo_queries.sql`: individual queries for the demonstration.

## Presentation

- `Applebees_Phase2_EN.pptx`: eight main slides plus two question appendices.
- `PRESENTATION_SCRIPT_EN.md`: timed English speaking notes.

## Local evidence

- `source_audit.json`: independent full-source aggregate audit; not a Spark runtime claim.
- `source_manifest.json`: input file inventory and SHA256 values.
- `test_pipeline_contracts.py`: local fixture and structure checks.
- `verify_sources.py`: independent source audit implementation; pass the dataset directory.
- `local_validation.json`: local check results and explicit runtime limitations.
- `test_jsonl_preparation.py`: bounded/lossless conversion, cache validation and failure-recovery tests.
- `jsonl_conversion_validation.json`: every record of the largest source file compared locally with JSONL output; not a Spark run.
- `runtime_troubleshooting.json`: observed dry-run success, first-update memory failure and pending runtime verification of the fix.

Historical Week 4 documents, notebooks and aggregate reports have `historical_`
prefixes. `migration_map.json` maps their original paths. They are not pipeline
libraries. Private individual transaction/employee evidence is not in this folder.
