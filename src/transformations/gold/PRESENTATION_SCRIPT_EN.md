# Five-minute English presentation script

Eight main slides and two appendix slides for questions. The speaking text has approximately 582 words.

## Slide 1

00:00–00:25. If you flagged a restaurant check as suspicious, could you trace every number back to its source? Our Phase 2 pipeline provides that foundation. We processed 2,142,846 checks from 127 locations across 115 days. Today I will show how the workflow preserves the data, validates its outputs and supports focused operational review.

Sources and scope: runtime_evidence.json, runtime_job_1_validation.csv and source_audit.json. Scope: 2026-04-28 through 2026-08-20.

## Slide 2

00:25–01:00. The source contains complete daily JSON arrays. Our first processing attempt exceeded the JSON reader’s memory. We added a preparation task that reads one check at a time and writes smaller files, with one check per JSON line. Silver standardizes fields and enriches them with location and channel references. Gold prepares reporting metrics. A separate acceptance task reconciles the results. Every stage retains the original file lineage.

Sources and scope: prepare_checks_jsonl_source.py, mv_checks_cleaned.py and the two Gold SQL libraries. Preparation source inventory SHA256 matches the independent audit.

## Slide 3

01:00–01:40. The transformations preserve the meaning of a check. We identify it with business date, location and check ID together. Payments and discounts become separate child tables, so expanding one array cannot multiply the other. A check’s tip equals the sum of its payment Gratuity values. We compare the magnitude of that sum because the usual source sign is negative. We also keep ticket discounts separate from item discounts until the business confirms whether their amounts overlap.

Sources and scope: DATA_CONTRACT.md and mv_checks_cleaned.py. EmployeeId in a payment identifies its actor, without a verified waiter-role mapping.

## Slide 4

01:40–02:20. Each quality rule has a defined response. Invalid reference dimensions stop publication. Unusable checks retain their evidence in quarantine, and the acceptance task rejects a nonempty quarantine. Empty payment lists remain visible for investigation. The accepted run contains all 2,142,846 checks, with zero duplicate keys, corrupt records or missing dates. We retained 3,856 checks with empty payment lists. That describes missing records in this export. Accounting reconciliation must establish whether customers actually paid.

Sources and scope: runtime_job_1_validation.csv and mv_quality_metrics.sql. Blocking results all passed. Empty payment lists remain in the published population.

## Slide 5

02:20–02:55. The job runs three tasks in order: prepare the files, refresh the pipeline, then validate its outputs. Each task requires the previous task to succeed. The first complete job finished successfully in 19 minutes and 34 seconds. All 28 audit results passed. Its source and published-check fingerprints matched the prior accepted manual run. Bounded retries handle processing failures. Failed data checks require review, and the job remains manually triggered during verification.

Sources and scope: runtime_evidence.json and runtime_job_1_validation.csv. Job ID 54448068766203. Run ID 469997930036472. Screenshot duration 19m 34s. All 28 audit rows passed, including 24 blocking results. A second full job run is still pending evidence.

## Slide 6

02:55–03:30. Our engineering choices fit the current source. Batch suits a fixed historical export. Materialized views store computed reporting results and refresh them through Lakeflow. Liquid clustering uses business date and location, which match common filters. Query profiles are still needed to measure its performance benefit. Expectations distinguish monitored exceptions from blocking integrity failures. Preparation reuses verified output files, but still reads source and output bytes to check their hashes. Incremental ingestion is a future improvement.

Sources and scope: README.md engineering choices and https://docs.databricks.com/aws/en/ldp/concepts/refresh. Clustering configuration is implemented in code. No measured acceleration, cost reduction or full incremental-ingestion claim.

## Slide 7

03:30–04:20. The data supports a practical investigation priority. In the audited source and Week 4 analysis, locations 87, 1 and 141 account for 71.08 percent of checks with empty payment lists. That is their share of missing-payment cases. Their local missing-payment rates answer a separate question. We would reconcile the source-system records at those locations first. The accepted Gold coverage also confirms 268,590 discounted checks, or 12.53 percent of all checks. Explicit denominators help the business compare locations fairly and investigate exceptions without treating concentration as proof of misconduct.

Sources and scope: Location concentration: historical_reports_week4_tickets_sin_pago_por_sucursal.csv and source audit. Runtime coverage: runtime_job_1_validation.csv. Specific location concentration still uses the historical baseline until the Gold query export is captured.

## Slide 8

04:20–05:00. We now have a working workflow with traceable data and a passing acceptance audit. Payment and discount event counts reconcile with their parent checks, and the repeat test preserved the published-check fingerprint. The next business step is to resolve missing-payment records and confirm discount definitions and permissions. The next engineering step is to verify the second complete job run and measure each task’s cost and duration. This gives the team a reliable starting point for investigation and future anomaly models.

Sources and scope: runtime_evidence.json, runtime_job_1_validation.csv and RUBRIC_EVIDENCE.md. Fingerprint scope covers selected source fields and published checks. Gold totals reconcile separately. Second full job and performance evidence remain pending.

## Current verification boundary

The first complete job and its comparison with a prior manual run are verified. Keep the second complete job run pending until its screenshot and validator CSV are captured. Refresh this statement when that evidence arrives.
