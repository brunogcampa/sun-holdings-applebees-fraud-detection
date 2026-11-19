# Gold: analytical tables and the publication gate

## Pipeline libraries (declared in `resources/pipelines/lakeflow_pipeline.yml`)

- [`mv_executive_kpis.sql`](mv_executive_kpis.sql): 14 analytical materialized views:
  coverage, daily/location/channel metrics, tip statistics and outliers, discount
  catalog and top locations, missing payments, positive-tip evidence, and employee and
  manager activity (private, not a fraud classification).
- [`mv_quality_metrics.sql`](mv_quality_metrics.sql): 4 quality views: data quality
  counts, quality issues, duplicate keys and missing dates.

## Publication gate (job task 3, `validate_outputs`)

- [`validate_pipeline.ipynb`](validate_pipeline.ipynb): importable notebook run by the job.
- [`validate_pipeline_source.py`](validate_pipeline_source.py): the same gate as source code
  (distinct base name for Databricks Git folder compatibility).

The gate runs 28 audits (population, reconciliation, uniqueness, completeness and
same-source fingerprints) and writes them to `pipeline_validation_runs`. Exported
results are in [`evidence/`](../../../evidence/).

These files stay in this folder because the live Databricks job and pipeline
reference these exact paths. Grains and formulas: [data contract](../../../docs/DATA_CONTRACT.md).
