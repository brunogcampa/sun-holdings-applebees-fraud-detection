"""Lakeflow batch materialized views. Historical EDA notebooks remain unchanged."""
from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(name="silver_checks_raw", comment="JSON source with file lineage; invalid dates retained")
def silver_checks_raw():
    root = spark.conf.get("applebees.source_root").rstrip("/")
    start = spark.conf.get("applebees.start_date")
    end = spark.conf.get("applebees.end_date")
    raw = (spark.read.option("multiLine", "true").option("mode", "FAILFAST")
           .option("recursiveFileLookup", "true").option("pathGlobFilter", "*.json")
           .json(root + "/facts/checks")
           .select("*", F.col("_metadata.file_path").alias("source_file"))
           .withColumn("business_date", F.expr("try_cast(BusinessDate as date)")))
    return raw.filter(F.col("business_date").between(start, end) | F.col("business_date").isNull())


def array_sum(expression):
    return F.expr("coalesce(aggregate(" + expression + ", cast(0 as double), (acc, x) -> acc + coalesce(cast(x as double), cast(0 as double))), cast(0 as double))")

@dp.materialized_view(name="silver_checks", comment="One row per source check; signed amounts retained")
@dp.expect_all({"check_id_present": "check_id IS NOT NULL", "location_present": "LocationId IS NOT NULL", "date_valid": "business_date IS NOT NULL"})
def silver_checks():
    raw = spark.read.table("silver_checks_raw")
    ticket_discounts = "transform(Discounts, x -> x.Amount)"
    item_discounts = "flatten(transform(ItemsSold, i -> coalesce(transform(i.Discounts, d -> d.Amount), array())))"
    has_item_discount = F.expr("coalesce(exists(ItemsSold, i -> coalesce(size(i.Discounts), 0) > 0), false)")
    return raw.select(
        F.col("Id").alias("check_id"), "LocationId", "RevenueCenterId", "BusinessDate", "business_date", "source_file",
        F.coalesce(F.size("Payments"), F.lit(0)).alias("payment_count"),
        F.coalesce(F.size("ItemsSold"), F.lit(0)).alias("item_count"),
        F.coalesce(F.size("Discounts"), F.lit(0)).alias("check_discount_count"),
        F.expr("coalesce(aggregate(ItemsSold, 0, (acc, i) -> acc + coalesce(size(i.Discounts), 0)), 0)").alias("item_discount_count"),
        F.coalesce(F.size("Voids"), F.lit(0)).alias("void_record_count"),
        ((F.coalesce(F.size("Discounts"), F.lit(0)) > 0) | has_item_discount).alias("has_discount"),
        array_sum("transform(Payments, p -> p.Amount)").alias("payment_amount_raw"),
        array_sum("transform(Payments, p -> p.Gratuity)").alias("gratuity_raw"),
        array_sum(ticket_discounts).alias("check_discount_amount_raw"),
        array_sum(item_discounts).alias("item_discount_amount_raw"),
        F.col("Payments").isNull().alias("payments_null"),
        F.col("ItemsSold").isNull().alias("items_null"),
        F.col("Discounts").isNull().alias("discounts_null"),
        F.col("TrafficCount"),
        F.expr("try_cast(OpenTime as timestamp)").alias("open_time"),
        F.expr("try_cast(CloseTime as timestamp)").alias("close_time"))
