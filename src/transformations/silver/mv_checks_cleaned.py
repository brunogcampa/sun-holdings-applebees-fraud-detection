"""Lakeflow source definitions. Execute as a pipeline library, not as a notebook.

Batch input is intentional: the supplied files contain complete multiline JSON arrays.
Data quality warnings preserve evidence. Hard key/reference failures route to quarantine.
"""
from pyspark import pipelines as dp
from pyspark.sql import functions as F, Window

DISCOUNT = "STRUCT<Amount:DOUBLE,DiscountId:BIGINT,DiscountName:STRING,EmployeeId:BIGINT,ManagerId:BIGINT>"
PAYMENT = "STRUCT<Amount:DOUBLE,Gratuity:DOUBLE,EmployeeId:BIGINT,PaymentCategoryId:BIGINT,PayCatName:STRING>"
ITEM = "STRUCT<ItemId:BIGINT,ItemName:STRING,Quantity:DOUBLE,GrossPrice:DOUBLE,SoldPrice:DOUBLE,EmployeeId:BIGINT,Sequence:BIGINT,Discounts:ARRAY<" + DISCOUNT + ">>"
SCHEMA = ("Id BIGINT, LocationId BIGINT, BusinessDate STRING, RevenueCenterId BIGINT, "
          "OpenTime STRING, CloseTime STRING, TrafficCount DOUBLE, ServiceCharge DOUBLE, "
          "Payments ARRAY<" + PAYMENT + ">, Discounts ARRAY<" + DISCOUNT + ">, "
          "ItemsSold ARRAY<" + ITEM + ">, Voids ARRAY<STRUCT<Amount:DOUBLE,EmployeeId:BIGINT,ManagerId:BIGINT>>, "
          "_corrupt_record STRING")


def root():
    return spark.conf.get("applebees.source_root").rstrip("/")


def json_source(path, schema):
    return (spark.read.schema(schema).option("multiLine", "true")
            .option("mode", "PERMISSIVE").option("recursiveFileLookup", "true")
            .option("pathGlobFilter", "*.json").json(root() + path)
            .select("*", F.col("_metadata.file_path").alias("source_file")))


@dp.materialized_view(name="silver_checks_raw", comment="Selected source fields with explicit types and file lineage")
@dp.expect("parseable_source", "_corrupt_record IS NULL")
def silver_checks_raw():
    return json_source("/facts/checks", SCHEMA)


@dp.materialized_view(name="silver_locations", comment="Location names and IDs; duplicate IDs block publication")
@dp.expect_or_fail("location_id_present", "Id IS NOT NULL")
@dp.expect_or_fail("location_id_unique", "id_count = 1")
def silver_locations():
    return json_source("/dimensions/locations", "Id BIGINT, Name STRING").withColumn(
        "id_count", F.count("*").over(Window.partitionBy("Id")))


@dp.materialized_view(name="silver_channels", comment="Revenue center reference; no assumed sales channel mapping")
@dp.expect_or_fail("channel_id_present", "Id IS NOT NULL")
@dp.expect_or_fail("channel_id_unique", "id_count = 1")
def silver_channels():
    return json_source("/dimensions/revenue_centers", "Id BIGINT, Name STRING").withColumn(
        "id_count", F.count("*").over(Window.partitionBy("Id")))


def total(expression):
    # Legacy-compatible numeric sum. Availability flags distinguish unknown inputs from true zero.
    return F.expr("coalesce(aggregate(" + expression + ",cast(0 AS DOUBLE),"
                  "(a,x)->a+coalesce(x,cast(0 AS DOUBLE))),cast(0 AS DOUBLE))")


@dp.materialized_view(name="silver_checks_assessed", comment="All source checks with quality reasons, scope and duplicate flags")
@dp.expect_all({
    "valid_key": "business_date IS NOT NULL AND check_id IS NOT NULL AND LocationId IS NOT NULL",
    "unique_check_key": "key_count = 1",
    "valid_location_reference": "location_ref_valid",
    "valid_channel_reference": "channel_ref_valid",
    "payment_list_present": "NOT payments_null",
    "payment_record_available": "payment_count > 0",
    "payment_numeric_fields": "payment_numeric_nulls = 0",
    "discount_numeric_fields": "discount_numeric_nulls = 0",
    "valid_open_time": "open_time IS NOT NULL",
    "valid_close_time": "close_time IS NOT NULL",
    "chronological_times": "close_time IS NULL OR open_time IS NULL OR close_time >= open_time",
})
def silver_checks_assessed():
    raw = spark.read.table("silver_checks_raw")
    df = raw.select(
        F.col("Id").alias("check_id"), "LocationId", "RevenueCenterId", "BusinessDate", "source_file", "_corrupt_record",
        F.expr("try_cast(BusinessDate AS DATE)").alias("business_date"),
        F.expr("try_cast(OpenTime AS TIMESTAMP)").alias("open_time"),
        F.expr("try_cast(CloseTime AS TIMESTAMP)").alias("close_time"),
        F.col("Payments").isNull().alias("payments_null"),
        F.col("ItemsSold").isNull().alias("items_null"),
        F.col("Discounts").isNull().alias("discounts_null"),
        F.expr("coalesce(array_size(Payments),0)").alias("payment_count"),
        F.expr("coalesce(array_size(ItemsSold),0)").alias("item_count"),
        F.expr("coalesce(array_size(Discounts),0)").alias("check_discount_count"),
        F.expr("coalesce(aggregate(ItemsSold,0,(a,i)->a+coalesce(array_size(i.Discounts),0)),0)").alias("item_discount_count"),
        F.expr("coalesce(array_size(Voids),0)").alias("void_record_count"),
        total("transform(Payments,p->p.Amount)").alias("payment_amount_raw"),
        total("transform(Payments,p->p.Gratuity)").alias("gratuity_raw"),
        total("transform(Discounts,d->d.Amount)").alias("check_discount_amount_raw"),
        total("flatten(transform(ItemsSold,i->coalesce(transform(i.Discounts,d->d.Amount),array())))").alias("item_discount_amount_raw"),
        F.expr("coalesce(array_size(filter(Payments,p->p IS NULL OR p.Amount IS NULL OR p.Gratuity IS NULL)),0)").alias("payment_numeric_nulls"),
        F.expr("coalesce(array_size(filter(Discounts,d->d IS NULL OR d.Amount IS NULL)),0)+coalesce(aggregate(ItemsSold,0,(a,i)->a+coalesce(array_size(filter(i.Discounts,d->d IS NULL OR d.Amount IS NULL)),0)),0)").alias("discount_numeric_nulls"))
    locations = spark.read.table("silver_locations").select(F.col("Id").alias("LocationId"), F.col("Name").alias("location_name"), F.lit(True).alias("location_ref_valid"))
    channels = spark.read.table("silver_channels").select(F.col("Id").alias("RevenueCenterId"), F.col("Name").alias("channel_name"), F.lit(True).alias("channel_ref_valid"))
    df = (df.join(locations, "LocationId", "left").join(channels, "RevenueCenterId", "left")
          .withColumn("key_count", F.count("*").over(Window.partitionBy("business_date", "LocationId", "check_id"))))
    start = spark.conf.get("applebees.start_date")
    end = spark.conf.get("applebees.end_date")
    df = (df.withColumn("in_scope", F.coalesce(F.col("business_date").between(start, end), F.lit(False)))
          .withColumn("has_discount", (F.col("check_discount_count") + F.col("item_discount_count")) > 0)
          .withColumn("tip_available", (~F.col("payments_null")) & (F.col("payment_count") > 0) & (F.col("payment_numeric_nulls") == 0)))
    reasons = [
        (F.col("_corrupt_record").isNotNull(), "CORRUPT_JSON_OR_TYPE"),
        (F.col("business_date").isNull(), "INVALID_DATE"),
        (F.col("check_id").isNull(), "MISSING_CHECK_ID"),
        (F.col("LocationId").isNull(), "MISSING_LOCATION_ID"),
        (F.col("location_ref_valid").isNull(), "UNKNOWN_LOCATION"),
        (F.col("channel_ref_valid").isNull(), "UNKNOWN_CHANNEL"),
        (F.col("key_count") > 1, "DUPLICATE_COMPOSITE_KEY"),
        (F.col("payment_numeric_nulls") > 0, "INVALID_PAYMENT_NUMERIC"),
        (F.col("discount_numeric_nulls") > 0, "INVALID_DISCOUNT_NUMERIC"),
        (F.col("items_null"), "MISSING_ITEM_LIST"),
        (F.col("discounts_null"), "MISSING_DISCOUNT_LIST"),
    ]
    return df.withColumn("quality_reasons", F.filter(F.array(*[F.when(condition, F.lit(reason)) for condition, reason in reasons]), lambda x: x.isNotNull()))


@dp.materialized_view(name="silver_checks", comment="Valid in-scope checks. Empty payment arrays retained as operational exceptions", cluster_by=["business_date", "LocationId"])
@dp.expect_or_fail("valid_published_check", "array_size(quality_reasons) = 0 AND in_scope AND key_count = 1")
def silver_checks():
    return spark.read.table("silver_checks_assessed").filter("in_scope AND array_size(quality_reasons) = 0")


@dp.materialized_view(name="silver_checks_quarantine", comment="Unusable records retained with reasons; no automatic deduplication")
def silver_checks_quarantine():
    return spark.read.table("silver_checks_assessed").filter("array_size(quality_reasons) > 0")


@dp.materialized_view(name="silver_checks_out_of_scope", comment="Valid records outside the configured period")
def silver_checks_out_of_scope():
    return spark.read.table("silver_checks_assessed").filter("NOT in_scope AND array_size(quality_reasons) = 0")


def accepted_raw():
    valid = spark.read.table("silver_checks").select("business_date", "LocationId", "check_id")
    raw = (spark.read.table("silver_checks_raw").withColumnRenamed("Id", "check_id")
           .withColumn("business_date", F.expr("try_cast(BusinessDate AS DATE)")))
    return raw.join(valid, ["business_date", "LocationId", "check_id"], "left_semi")


@dp.materialized_view(name="silver_discount_events", comment="Discount events expanded separately by level and source position")
def silver_discount_events():
    raw = accepted_raw()
    keys = ["business_date", "LocationId", "check_id", "source_file"]
    ticket = raw.select(*keys, F.posexplode("Discounts").alias("discount_position", "discount"))
    ticket = ticket.withColumn("item_position", F.lit(None).cast("int")).withColumn("discount_level", F.lit("ticket"))
    items = raw.select(*keys, F.posexplode("ItemsSold").alias("item_position", "item"))
    item = items.select(*keys, "item_position", F.posexplode("item.Discounts").alias("discount_position", "discount"))
    item = item.withColumn("discount_level", F.lit("item"))
    cols = keys + ["item_position", "discount_position", "discount_level", "discount.*"]
    return ticket.select(*cols).unionByName(item.select(*cols)).withColumn("discount_name_normalized", F.upper(F.trim("DiscountName")))


@dp.materialized_view(name="silver_payments", comment="One row per payment. EmployeeId is the payment actor, not a validated waiter role")
def silver_payments():
    return accepted_raw().select("business_date", "LocationId", "check_id", "RevenueCenterId", "source_file",
                                 F.posexplode("Payments").alias("payment_position", "payment")).select(
        "business_date", "LocationId", "check_id", "RevenueCenterId", "source_file", "payment_position", "payment.*")
