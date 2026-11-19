# Tests and source audit

Local checks that need no Spark. Run them from the repository root.

| File | What it checks |
|---|---|
| [`test_pipeline_contracts.py`](test_pipeline_contracts.py) | Quality-rule fixtures, repository structure, LF line endings, Python syntax, the three pipeline libraries, job dependencies, Gold → Silver dependencies, clean notebooks, runtime paths and Markdown links |
| [`test_jsonl_preparation.py`](test_jsonl_preparation.py) | Lossless, bounded JSONL conversion, cache validation and failure recovery |
| [`verify_sources.py`](verify_sources.py) | Independent full-source audit: `python tests/verify_sources.py PATH_TO_DATASET` |

```bash
python -B tests/test_pipeline_contracts.py
python -B tests/test_jsonl_preparation.py
```

Spark execution is verified in Databricks by the job's validation gate. See [`evidence/`](../evidence/).
