# Phase 2 rubric and evidence register

The assignment requires working runtime evidence as well as organized source code.
This register distinguishes verified evidence from pending Databricks actions.

| Criterion | Implementation and explanation | Evidence available now | Runtime evidence still required |
|---|---|---|---|
| GitHub repository and documentation | Exact four leaf directories; bundle entry point; root navigation; runbook; contracts; historical migration map | Source files, Passing local fixture, preparation and repository tests, Git history | Confirm a reviewer can access the private repository |
| Job and pipeline design | Source preparation followed by triggered Lakeflow graph and validator task; one concurrent run; paused schedule; bounded retry | Two YAML files, dependency and recovery documentation | Job graph, successful pipeline update, run IDs, observed durations |
| Transformations and table value | Explicit schemas, date parsing, reference enrichment, composite keys, quarantine, separate child events, Gold reporting grains | Three pipeline libraries, table catalog and analytical definitions | Graph/table previews and parent-child reconciliation results |
| Streaming, materialized views, liquid clustering and expectations | Batch justified by static multiline export; materialized views; date/location clustering; warn/fail rules | Configuration and documented tradeoffs | Actual expectations results and clustering settings; query profiles before performance claims |
| Data quality checks | Missing keys, types, dates, duplicates, references, list/numeric availability, scope, timestamps, reconciliation | Full-source Python audit and synthetic failure fixtures | Quarantine/expectations views and validator audit from Databricks |
| Analysis, insights and business value | Concentration of missing-payment cases, discount denominators, tip sign/magnitude and location/category comparisons | Reproduced historical baseline and source-linked historical aggregate reports | Run demo SQL on accepted Gold and refresh presentation figures |
| Technical communication | Eight main slides for five minutes; evidence/source distinctions; definitions and questions appendix | English speaking script and live deck | Rehearsal and runtime screenshots once available |

## Current verification

- Independent audit: all 115 input files, 2,142,846 checks, 127 locations, 115 days.
- Composite duplicate keys: zero in the source audit.
- Core missing-field/reference rules: zero affected rows in the independent audit.
- Empty Payments: 3,856. Null Payments: zero. These are distinct observations.
- Discount events: 240,699 ticket / 275,991 item. Payment events: 2,232,092.
- Tip signs: 1,029,262 negative / 1,113,581 zero / 3 positive aggregate checks.
- Local tests cover fixtures, lossless bounded preparation, failure recovery and repository contracts; see `local_validation.json`. They do not execute Spark.
- Databricks dry run: **PASSED**, based on the user-provided screenshot.
- First processing update: **FAILED** with Photon JSON-scan out-of-memory; downstream flows skipped.
- Bounded JSONL fix: **IMPLEMENTED AND LOCALLY TESTED**; successful Databricks update remains **PENDING**.
- Bundle CLI validation and actual SQL/Spark execution: **PENDING**.
- Job run and same-source rerun: **PENDING**.
- Measured latency/cost improvement and fraud detection accuracy: **NOT CLAIMED**.

## Evidence to capture after deployment

| Evidence ID | Capture | Acceptance criterion |
|---|---|---|
| R1 | Repository root and four required leaf directories | Code/config/docs easy to navigate |
| P1 | Lakeflow graph and update ID | All required datasets refresh successfully |
| J1 | Job graph | Validator depends on successful pipeline task |
| J2 | First and second successful run IDs | Both accepted; same-source rerun consistency true |
| Q1 | Quality/expectations results | No unexplained hard-rule failures |
| Q2 | `pipeline_validation_runs` rows | Reconciliation and original-snapshot checks pass |
| A1 | Gold query/chart results | Match displayed populations, filters and denominators |
| E1 | Clustering settings/query profile | Confirm implementation; document measured effect if claimed |

Keep transactional/actor evidence private. Screenshots should hide personal data
without hiding update/run IDs, task states or relevant technical context.

## Submission readiness gate

The package is ready for deployment and review. It is **not a fully runtime-verified
Phase 2 submission** until P1, J1, J2, Q1, Q2 and A1 have been captured. No template
or presentation wording may turn those pending checks into claimed accomplishments.
