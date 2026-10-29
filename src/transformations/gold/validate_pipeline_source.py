# Databricks notebook source
# MAGIC %md
# MAGIC # Phase 2 publication gate
# MAGIC Run after the Lakeflow pipeline. A failed hard check fails this task.
# MAGIC Audit results stay in the private output schema. No employee names are exported.

# COMMAND ----------
from datetime import datetime, timezone
import json
import re
import uuid
from pyspark.sql import functions as F
dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "applebees_phase2")
dbutils.widgets.text("run_id", "manual")
dbutils.widgets.text("validate_original_snapshot", "true")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
assert all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", x) for x in [catalog, schema])
prefix = f"`{catalog}`.`{schema}`."
run_id = dbutils.widgets.get("run_id")
if run_id == "manual":
    run_id = "manual_" + uuid.uuid4().hex
timestamp = datetime.now(timezone.utc).isoformat()
checks = []


def scalar(query):
    return spark.sql(query).first()[0]


def record(name, actual, expected, passed, severity="ERROR"):
    checks.append((run_id, timestamp, name, str(actual), str(expected), passed, severity))


def equal(name, actual, expected):
    record(name, actual, expected, actual == expected)


def table(name):
    return prefix + "`" + name + "`"

# COMMAND ----------
dq = spark.table(f"{catalog}.{schema}.gold_data_quality").first().asDict()
coverage = spark.table(f"{catalog}.{schema}.gold_coverage").first().asDict()
raw_rows = scalar(f"SELECT count(*) FROM {table('silver_checks_raw')}")
equal("source_rows_assessed", dq["assessed_rows"], raw_rows)
equal("all_source_rows_accounted_for", dq["published_rows"] + dq["quarantined_rows"] + dq["out_of_scope_rows"], raw_rows)
equal("published_population", coverage["tickets"], dq["published_rows"])
equal("gold_daily_reconciles", scalar(f"SELECT coalesce(sum(tickets),0) FROM {table('gold_daily_metrics')}"), coverage["tickets"])
equal("gold_locations_reconcile", scalar(f"SELECT coalesce(sum(tickets),0) FROM {table('gold_location_metrics')}"), coverage["tickets"])
equal("gold_channels_reconcile", scalar(f"SELECT coalesce(sum(tickets),0) FROM {table('gold_channel_metrics')}"), coverage["tickets"])
equal("missing_dates", scalar(f"SELECT count(*) FROM {table('gold_missing_dates')}"), 0)
equal("published_key_duplicates", scalar(f"SELECT count(*) FROM (SELECT business_date,LocationId,check_id FROM {table('silver_checks')} GROUP BY business_date,LocationId,check_id HAVING count(*)>1)"), 0)
equal("corrupt_source_records", dq["corrupt_records"], 0)
equal("quarantined_rows", dq["quarantined_rows"], 0)
for level, field in [("ticket", "check_discount_count"), ("item", "item_discount_count")]:
    parent_count = scalar(f"SELECT coalesce(sum({field}),0) FROM {table('silver_checks')}")
    child_count = scalar(f"SELECT count(*) FROM {table('silver_discount_events')} WHERE discount_level='{level}'")
    equal(level + "_event_reconciliation", child_count, parent_count)
equal("payment_event_reconciliation", scalar(f"SELECT count(*) FROM {table('silver_payments')}"),
      scalar(f"SELECT coalesce(sum(payment_count),0) FROM {table('silver_checks')}"))
payment_totals = spark.sql(f"SELECT sum(Amount) AS amount,sum(Gratuity) AS tip FROM {table('silver_payments')}").first()
check_totals = spark.sql(f"SELECT sum(payment_amount_raw) AS amount,sum(gratuity_raw) AS tip FROM {table('silver_checks')}").first()
for field in ["amount", "tip"]:
    delta = abs(float(payment_totals[field] or 0) - float(check_totals[field] or 0))
    record("payment_" + field + "_sum_reconciliation", delta, "<= 0.01 (double aggregation tolerance)", delta <= .01)
record("empty_payment_lists_monitor", dq["empty_payment_lists"], "Monitor; retained for investigation", True, "WARN")
record("timestamp_issues_monitor", dq["invalid_open_times"] + dq["invalid_close_times"] + dq["close_before_open"],
       "Review affected records; no automatic correction", True, "WARN")

# COMMAND ----------
if dbutils.widgets.get("validate_original_snapshot").lower() == "true":
    expected = {"tickets": 2142846, "locations": 127, "observed_days": 115,
                "discounted_tickets": 268590, "empty_payment_lists": 3856}
    for metric, value in expected.items():
        equal("original_snapshot_" + metric, coverage[metric], value)
    for level, count in [("ticket", 240699), ("item", 275991)]:
        equal("original_snapshot_" + level + "_events", scalar(f"SELECT count(*) FROM {table('silver_discount_events')} WHERE discount_level='{level}'"), count)

# COMMAND ----------
# Deterministic fingerprints allow the SECOND run to demonstrate rerun consistency.
def fingerprint(name):
    row = spark.sql(f"SELECT count(*) AS n,coalesce(sum(cast(xxhash64(to_json(struct(*))) AS DECIMAL(38,0))),0) AS h FROM {table(name)}").first()
    return str(row["n"]) + ":" + str(row["h"])


source_signature = fingerprint("silver_checks_raw")
output_signature = fingerprint("silver_checks")
record("source_fingerprint", source_signature, "Versioned source snapshot", True, "INFO")
record("output_fingerprint", output_signature, "Published check snapshot", True, "INFO")
audit_name = f"{catalog}.{schema}.pipeline_validation_runs"
prior = None
if spark.catalog.tableExists(audit_name):
    prior = spark.sql(f"""SELECT s.actual AS source_hash,o.actual AS output_hash
      FROM {table('pipeline_validation_runs')} s
      JOIN {table('pipeline_validation_runs')} o USING(run_id)
      JOIN {table('pipeline_validation_runs')} c USING(run_id)
      WHERE s.metric='source_fingerprint' AND o.metric='output_fingerprint'
        AND c.metric='run_complete' AND c.passed=true AND s.run_id <> '{run_id.replace(chr(39), chr(39)*2)}'
      ORDER BY s.recorded_at DESC LIMIT 1""").first()
if prior is None:
    record("same_source_rerun_consistency", "FIRST_RUN", "Run again with the same sources", None, "INFO")
elif prior["source_hash"] == source_signature:
    equal("same_source_rerun_consistency", output_signature, prior["output_hash"])
else:
    record("same_source_rerun_consistency", "SOURCE_CHANGED", "Repeat unchanged source before asserting idempotence", None, "INFO")
hard_failures = [r[2] for r in checks if r[5] is False and r[6] == "ERROR"]
record("run_complete", not hard_failures, True, not hard_failures)
audit = spark.createDataFrame(checks, "run_id string, recorded_at string, metric string, actual string, expected string, passed boolean, severity string")
audit.createOrReplaceTempView("phase2_validation_update")
spark.sql(f"CREATE TABLE IF NOT EXISTS {table('pipeline_validation_runs')} (run_id STRING,recorded_at STRING,metric STRING,actual STRING,expected STRING,passed BOOLEAN,severity STRING) USING DELTA")
spark.sql(f"""MERGE INTO {table('pipeline_validation_runs')} t USING phase2_validation_update s
 ON t.run_id=s.run_id AND t.metric=s.metric WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *""")
display(audit)
assert not hard_failures, "Publication gate failed: " + ", ".join(hard_failures)
print(json.dumps({"run_id":run_id,"status":"PASSED","schema":f"{catalog}.{schema}","first_run":prior is None}))
