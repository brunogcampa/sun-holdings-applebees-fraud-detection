# Read-only queries

Run these in the Databricks SQL editor against `workspace.applebees_phase2`. They
inspect results and change nothing.

| File | Purpose |
|---|---|
| [`demo_queries.sql`](demo_queries.sql) | Individual queries for the live demonstration |
| [`diagnose_pipeline.sql`](diagnose_pipeline.sql) | Stage counts that detect incomplete populations (read = assessed = published) |
| [`final_gold_evidence.sql`](final_gold_evidence.sql) | Produces the 15-row Gold export in [`evidence/runtime_gold_evidence.csv`](../../evidence/runtime_gold_evidence.csv) |
| [`job_run_audit.sql`](job_run_audit.sql) | Reads `pipeline_validation_runs` for one job run; change the run ID to inspect another |
