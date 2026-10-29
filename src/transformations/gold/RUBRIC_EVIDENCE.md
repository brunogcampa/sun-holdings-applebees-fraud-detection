# Phase 2 rubric and verified evidence

Verification date: October 29, 2026. Runtime evidence comes from user-operated
Databricks executions, exported CSVs and screenshots. Local tests remain separate.

| Criterion | Implementation | Verified evidence | Limitations or follow-up |
|---|---|---|---|
| Repository and documentation | Four required leaf directories, source logic, YAML, runbook, contracts and SQL | Code cloned and executed in Databricks. Local structure and LF checks pass | Repository is private. Evaluator access must be confirmed |
| Job and pipeline design | Success dependencies between preparation, refresh and validation. Bounded retries | Job 54448068766203 succeeded twice, with all three tasks green and 28 audit results passing per run | Runs were manually triggered. YAML daily schedule remains a paused proposal |
| Transformations and table value | Explicit types, composite keys, reference enrichment and independent child arrays | All 2,142,846 rows preserved. Payment and discount child counts reconcile | Business definitions of source amount signs, currency and actor roles require confirmation |
| Engineering practices | Bounded JSONL preparation, batch materialized views, date/location clustering and expectations | 27 datasets refreshed, original file lineage retained and unchanged-source fingerprints preserved | Clustering is configured in code. Query profiles and measured speed/cost gains are not claimed |
| Data quality | Missing/type/key/reference rules, quarantine, timestamp/payment monitoring and audit gate | Zero duplicate keys, corrupt records, quarantine and missing dates. 3,856 empty payment lists retained | POS/ledger reconciliation is a business follow-up |
| Analysis and business value | Gold coverage, location comparisons, tip magnitudes and IQR outliers | 268,590 discounted checks. Top 3 locations hold 71.0840% of empty-payment cases. 77,856 high-tip outliers above 17.5 | Concentration and statistical outliers are review signals, with explicit denominators |
| Communication | README, business findings, source notes, runbook and evidence links | Latest results and both runs are documented | Existing presentation assets remain an earlier snapshot. Runtime evidence is authoritative |

## Runtime evidence register

| Evidence ID | Status | Evidence |
|---|---|---|
| P1 | PASSED | Screenshots of all 27 datasets and exact population SQL export |
| J1 | PASSED | Three-task job graph, ordered by success dependencies |
| J2 | PASSED | Runs 469997930036472 and 904398544867578 succeeded in 19m 34s and 21m 23s |
| Q1 | PASSED | Ten assessed rules met. The payment-record monitor flags 3,856 retained checks |
| Q2 | PASSED | Both full-job audit exports contain 28 passed results, including 24 blocking results each |
| A1 | PASSED | Final Gold query and its 15-row aggregate export reproduce coverage, location and tip findings |
| E1 | IMPLEMENTED AND EXPLAINED | Code and design rationale cover batch, materialized views, clustering and expectations. No unmeasured speed claim |

## Exact run evidence

| Run | Identifier | Observed duration | Audit |
|---|---|---|---|
| Prior manual gate | `manual_5ac8591deaee4c87ad21ca2d16dc38f1` | Not captured | [Manual validation](runtime_manual_validation.csv) |
| Complete job 1 | `469997930036472` | 19m 34s | [28 passed results](runtime_job_1_validation.csv) |
| Complete job 2 | `904398544867578` | 21m 23s | [28 passed results](runtime_job_2_validation.csv) |

- Job ID: `54448068766203`.
- Source fingerprint in all accepted runs: `2142846:3507863786310667794794`.
- Published-check fingerprint: `2142846:-2753200972392633748389`.
- Both complete jobs record `same_source_rerun_consistency=true` and `run_complete=true`.
- `severity=ERROR` labels a blocking rule. `passed=true` establishes its success.
- Payment events: 2,232,092. Discount events: 240,699 ticket and 275,991 item.
- Signed payment/tip sums reconcile within the declared 0.01 aggregation tolerance.
- Empty-payment monitor: 3,856. Timestamp issues: 0.
- Twenty-four local tests cover fixtures, bounded preparation and repository contracts.

## Supporting files and interpretation

- [Runtime summary](runtime_evidence.json)
- [Final Gold query](final_gold_evidence.sql)
- [Gold export](runtime_gold_evidence.csv)
- [Business findings and recommendations](BUSINESS_FINDINGS.md)
- [Data contract](DATA_CONTRACT.md)

The fingerprint covers selected raw fields and published checks. Gold totals
reconcile separately. These checks do not establish accounting accuracy against
the POS/ledger or bitwise identity of every Gold table. Detailed transactional
and actor records stay private in the volume and Databricks tables.

## Delivery and optional observability

Core technical acceptance and runtime evidence are complete. Confirm that the
evaluators can access the private repository before submitting its URL. Keep the
current manual-trigger setting unless a real new-data cadence is agreed. The
paused daily schedule in YAML is a deployment proposal.

Individual task timings, pipeline update IDs, exported workspace configuration
and clustering query profiles were not captured. They are useful observability
extensions, and no corresponding performance improvement is claimed.
