# Databricks notebook source
# MAGIC %md
# MAGIC # Publicar eventos de descuento para SQL
# MAGIC Ejecutar en orden. Lee el volumen original, conserva nivel y archivo de origen,
# MAGIC guarda una tabla Delta nueva y publica una vista reutilizable.
# MAGIC No elimina ni sobrescribe tablas históricas. Los datos detallados permanecen en Databricks.

# COMMAND ----------
from datetime import datetime, timezone
from pyspark.sql import functions as F
dbutils.widgets.text("data_root", "/Volumes/workspace/applebees_raw/source/applebees_source")
dbutils.widgets.text("start_date", "2026-04-28")
dbutils.widgets.text("end_date", "2026-08-20")
root = dbutils.widgets.get("data_root").rstrip("/")
start, end = dbutils.widgets.get("start_date"), dbutils.widgets.get("end_date")
assert root.startswith("/Volumes/")
assert datetime.fromisoformat(start) <= datetime.fromisoformat(end)
raw = (spark.read.option("multiLine", "true").option("mode", "FAILFAST")
       .option("recursiveFileLookup", "true").option("pathGlobFilter", "*.json")
       .json(root + "/facts/checks")
       .select("*", F.col("_metadata.file_path").alias("source_file"))
       .withColumn("business_date", F.expr("try_cast(BusinessDate as date)")))
raw = raw.filter(F.col("business_date").between(start, end) | F.col("business_date").isNull())

# COMMAND ----------
keys = ["business_date", "LocationId", "source_file"]
ticket = raw.select(*keys, F.col("Id").alias("check_id"), F.explode("Discounts").alias("discount"))
items = raw.select(*keys, F.col("Id").alias("check_id"), F.explode("ItemsSold").alias("item"))
item = items.select(*keys, "check_id", F.explode("item.Discounts").alias("discount"))
events = ticket.select(*keys, "check_id", "discount.*").withColumn("discount_level", F.lit("ticket")).unionByName(
    item.select(*keys, "check_id", "discount.*").withColumn("discount_level", F.lit("item")), allowMissingColumns=True)
run = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
target = "workspace.applebees_eda.discount_events_" + run
assert not spark.catalog.tableExists(target)
events.write.format("delta").mode("append").saveAsTable(target)
spark.sql("CREATE OR REPLACE VIEW workspace.applebees_eda.discount_events_current AS SELECT * FROM " + target)
display(spark.table(target).groupBy("discount_level").count())
print("Tabla histórica:", target)
print("Vista para SQL: workspace.applebees_eda.discount_events_current")
