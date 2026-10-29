# Phase 2 rubric and verified evidence

Verification date: October 29, 2026. Runtime evidence comes from the user-operated
Databricks workspace, exported CSVs and screenshots. Local tests remain separate.

| Criterion | Implemented evidence | Verified runtime result | Remaining evidence |
|---|---|---|---|
| GitHub and documentation | Four requested leaf directories, three pipeline libraries, runbook, contract and history | Code cloned and executed in Databricks | Evaluator access to the private repository |
| Job and pipeline design | Preparation, pipeline refresh and validator with success dependencies and bounded retries | Job 54448068766203, run 469997930036472 succeeded in 19m 34s | Second complete job, per-task durations and exported final configuration |
| Transformations and table value | Explicit types, composite keys, reference enrichment, separate payment/discount arrays and Gold reporting grains | All 2,142,846 checks preserved and parent-child counts reconciled | Gold operational-query export for displayed location concentration |
| Engineering practices | Batch justified by static source, bounded JSONL preparation, materialized views, clustering keys and expectations | 27 datasets refreshed, original file lineage preserved, unchanged-source fingerprints match | Observe clustering properties and query profiles before claiming acceleration |
| Data quality | Missing/type/key/reference rules, quarantine, timestamp and payment-list monitoring, audit gate | No duplicate keys, corrupt records, quarantine or missing dates. 3,856 empty payment lists retained | Internal POS/ledger reconciliation and source-system explanations |
| Analysis and business value | Explicit discount denominators, operational exceptions, location and actor concentration | Gold coverage confirms 268,590 discounted checks. Payment and discount events reconcile | Confirm discount permissions and exposure-adjusted investigation priorities |
| Communication | English five-minute script, eight main slides, two appendices and source notes | Presentation reflects first complete job and repeat comparison | Add second complete job evidence when available |

## Runtime evidence register

| Evidence ID | Status | Evidence |
|---|---|---|
| P1 | PASSED for data execution | 27 dataset screenshots and exact population SQL export. Pipeline update ID still to capture |
| J1 | PASSED | Screenshot of `prepare_sources`, `refresh_pipeline`, `validate_outputs` with success dependencies |
| J2 | PARTIAL | First complete job succeeded. It matches the prior accepted manual run. Second complete job awaits evidence |
| Q1 | PASSED | Ten assessed rules met. One monitored exception corresponds to empty payment lists. Published rows retained |
| Q2 | PASSED | Manual gate and all 28 first-job audit results passed, including 24 blocking results |
| A1 | PARTIAL | Coverage/event counts verified in Gold/Silver. Specific location-concentration export still to capture |
| E1 | IMPLEMENTED | Date/location clustering configured in code. No measured speed or cost improvement claimed |

## Exact evidence and interpretation

- [Runtime summary](runtime_evidence.json)
- [Manual gate CSV](runtime_manual_validation.csv)
- [Complete-job gate CSV](runtime_job_1_validation.csv)
- Manual accepted run: `manual_5ac8591deaee4c87ad21ca2d16dc38f1`.
- Complete job run: `469997930036472`. Observed total duration: 19m 34s.
- Source fingerprint: `2142846:3507863786310667794794` in both runs.
- Published-check fingerprint: `2142846:-2753200972392633748389` in both runs.
- The manual run recorded `FIRST_RUN`. The complete job records `same_source_rerun_consistency=true`.
- `severity=ERROR` labels a blocking rule. Its `passed=true` value establishes success.
- All 2,142,846 source rows are assessed and published. Quarantine and valid out-of-scope outputs contain zero rows.
- Discount events: 240,699 ticket and 275,991 item. Payment events: 2,232,092.
- Signed payment/tip sums reconcile within the declared 0.01 aggregation tolerance.
- `empty_payment_lists_monitor=3856` and `timestamp_issues_monitor=0` are intentional monitoring results.
- Twenty-four local tests cover fixtures, preparation and repository contracts. They do not substitute for the runtime exports.

The fingerprint covers selected raw fields and published checks, while Gold
totals reconcile separately. It does not establish bitwise equality of every Gold
dataset or accounting accuracy against the POS/ledger. Original and prepared
transactional files stay private in the volume.

## Remaining submission checks

Capture the second full job run and its audit, the pipeline update ID, per-task
durations and Gold operational-query results. Confirm evaluator access. Keep
manual triggering during verification. The paused 07:00 schedule in the bundle
is a deployment proposal, not an observed active workspace schedule.
