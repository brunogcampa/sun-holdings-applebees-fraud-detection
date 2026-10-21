"""Ticket and item discount arrays are expanded separately, avoiding a cross product."""
from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(name="silver_discount_events", comment="One row per observed discount event, with level and lineage")
def silver_discount_events():
    raw = spark.read.table("silver_checks_raw")
    keys = ["business_date", "LocationId", "source_file"]
    ticket = raw.select(*keys, F.col("Id").alias("check_id"), F.explode("Discounts").alias("discount"))
    items = raw.select(*keys, F.col("Id").alias("check_id"), F.explode("ItemsSold").alias("item"))
    item = items.select(*keys, "check_id", F.explode("item.Discounts").alias("discount"))
    return ticket.select(*keys, "check_id", "discount.*").withColumn("discount_level", F.lit("ticket")).unionByName(
        item.select(*keys, "check_id", "discount.*").withColumn("discount_level", F.lit("item")), allowMissingColumns=True)
