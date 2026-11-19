# Evidence

Aggregate exports from the Databricks runs of October 29, 2026, plus local audits.
They contain no individual check or employee records.

| File | Contents |
|---|---|
| [`runtime_evidence.json`](runtime_evidence.json) | Summary of preparation, publication, both complete jobs and the Gold analysis |
| [`runtime_job_1_validation.csv`](runtime_job_1_validation.csv) | 28 gate audits, run `469997930036472` (all passed) |
| [`runtime_job_2_validation.csv`](runtime_job_2_validation.csv) | 28 gate audits, run `904398544867578` (all passed) |
| [`runtime_manual_validation.csv`](runtime_manual_validation.csv) | Gate audits from the manual run before the second job |
| [`runtime_gold_evidence.csv`](runtime_gold_evidence.csv) | 15-row Gold export behind the business findings |
| [`runtime_troubleshooting.json`](runtime_troubleshooting.json) | Failure history and verified recovery |
| [`source_audit.json`](source_audit.json) | Independent full-source aggregate audit (local, not Spark) |
| [`source_manifest.json`](source_manifest.json) | Source file inventory with SHA256 values |
| [`jsonl_conversion_validation.json`](jsonl_conversion_validation.json) | Record-by-record comparison of the largest source file with its JSONL output |
| [`local_validation.json`](local_validation.json) | Local check results recorded on October 29, 2026 |

File paths mentioned inside these records reflect the repository layout at the time
they were produced. They are kept unchanged as evidence.
