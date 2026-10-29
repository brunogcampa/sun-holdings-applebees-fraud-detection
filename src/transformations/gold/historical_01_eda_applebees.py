# Databricks notebook source
# MAGIC %md
# MAGIC # Applebee's — EDA, Week 4
# MAGIC Exploración reproducible de cobertura, calidad, descuentos y propinas. Los resultados son observaciones, no confirmación de fraude. Ejecutar las celdas en orden. Los datos personales y resultados detallados permanecen en Databricks.

# COMMAND ----------
from pyspark.sql import functions as F
from datetime import datetime, timezone
dbutils.widgets.text("data_root", "", "Ruta del volumen con dimensions/ y facts/")
dbutils.widgets.text("output_schema", "", "Catálogo.esquema para resultados del EDA")
dbutils.widgets.text("start_date", "2026-04-28", "Fecha inicial")
dbutils.widgets.text("end_date", "2026-08-20", "Fecha final")
ROOT = dbutils.widgets.get("data_root").rstrip("/")
OUTPUT = dbutils.widgets.get("output_schema")
START = dbutils.widgets.get("start_date")
END = dbutils.widgets.get("end_date")
assert ROOT.startswith("/Volumes/"), "Completar data_root con la ruta del volumen."
assert len(OUTPUT.split(".")) == 2 and all(p.replace("_", "").isalnum() for p in OUTPUT.split(".")), "Indicar catálogo.esquema válido."
assert datetime.fromisoformat(START) <= datetime.fromisoformat(END)
RUN = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
print({"data_root": ROOT, "periodo_solicitado": [START, END], "run_utc": RUN})

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Lectura del JSON original
# MAGIC Los archivos contienen arreglos JSON completos: multiLine=true. Se conserva el archivo de origen. Las listas de pagos, productos y descuentos se agregan por separado, sin multiplicar filas.

# COMMAND ----------
raw = (spark.read.option("multiLine", "true").option("mode", "FAILFAST")
       .option("recursiveFileLookup", "true").option("pathGlobFilter", "*.json")
       .json(ROOT + "/facts/checks")
       .select("*", F.col("_metadata.file_path").alias("source_file")))
required = {"Id", "LocationId", "BusinessDate", "Payments", "ItemsSold", "Discounts", "Voids"}
assert required.issubset(set(raw.columns)), f"Faltan campos: {required - set(raw.columns)}"
raw.printSchema()
raw = raw.withColumn("business_date", F.expr("try_cast(BusinessDate as date)"))
# Mantener fechas inválidas para que el control de calidad las detecte.
raw = raw.filter(F.col("business_date").between(START, END) | F.col("business_date").isNull())

# COMMAND ----------
def array_sum(expression):
    return F.expr("coalesce(aggregate(" + expression + ", cast(0 as double), (acc, x) -> acc + coalesce(cast(x as double), cast(0 as double))), cast(0 as double))")

ticket_discounts = "transform(Discounts, x -> x.Amount)"
item_discounts = "flatten(transform(ItemsSold, i -> coalesce(transform(i.Discounts, d -> d.Amount), array())))"
has_item_discount = F.expr("coalesce(exists(ItemsSold, i -> coalesce(size(i.Discounts), 0) > 0), false)")
features = raw.select(
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
# No sumar importes de descuentos de ticket y de producto sin reconciliar su semántica.
# Persistir una tabla compacta por ejecución evita releer los JSON en cada gráfico.
FEATURE_TABLE = OUTPUT + ".eda_checks_" + RUN
assert not spark.catalog.tableExists(FEATURE_TABLE), "La tabla ya existe; iniciar una ejecución nueva."
features.write.format("delta").mode("append").saveAsTable(FEATURE_TABLE)
checks = spark.table(FEATURE_TABLE)
print("Tabla de esta ejecución:", FEATURE_TABLE)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Cobertura y calidad
# MAGIC El rango observado puede ser menor que el solicitado si la carga está incompleta. No se eliminan duplicados automáticamente. La ausencia de un ID no equivale a cero.

# COMMAND ----------
coverage = checks.agg(
    F.count("*").alias("tickets"), F.countDistinct("source_file").alias("archivos_leidos"),
    F.countDistinct("LocationId").alias("sucursales"), F.countDistinct("business_date").alias("dias_observados"),
    F.min("business_date").alias("desde"), F.max("business_date").alias("hasta"),
    F.sum(F.col("check_id").isNull().cast("long")).alias("ticket_id_nulo"),
    F.sum(F.col("LocationId").isNull().cast("long")).alias("location_id_nulo"),
    F.sum(F.col("business_date").isNull().cast("long")).alias("fecha_nula_o_invalida"),
    F.sum(F.col("payments_null").cast("long")).alias("lista_pagos_nula"),
    F.sum((F.col("payment_count") == 0).cast("long")).alias("sin_pagos"),
    F.sum((F.col("close_time") < F.col("open_time")).cast("long")).alias("cierre_anterior_apertura"))
display(coverage)
valid_keys = checks.filter(F.col("check_id").isNotNull() & F.col("LocationId").isNotNull() & F.col("business_date").isNotNull())
duplicates = valid_keys.groupBy("business_date", "LocationId", "check_id").count().filter("count > 1")
display(duplicates.agg(F.count("*").alias("claves_duplicadas"), F.coalesce(F.sum(F.col("count") - 1), F.lit(0)).alias("filas_excedentes")))
expected_dates = spark.range(1).select(F.explode(F.sequence(F.to_date(F.lit(START)), F.to_date(F.lit(END)))).alias("business_date"))
display(expected_dates.join(checks.select("business_date").distinct(), "business_date", "left_anti").orderBy("business_date"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Dimensiones: cobertura y referencias
# MAGIC Los resultados visibles usan conteos e identificadores; no muestran nombres ni fechas de nacimiento de empleados.

# COMMAND ----------
dimension_paths = {"locations": "locations/locations.json", "revenue_centers": "revenue_centers/revenueCenters.json", "items": "items/items.json", "employees": "employees/employees.json"}
dimensions = {}
for name, path in dimension_paths.items():
    dim = spark.read.option("multiLine", "true").option("mode", "FAILFAST").json(ROOT + "/dimensions/" + path)
    dimensions[name] = dim
    print("Dimensión:", name)
    display(dim.agg(F.count("*").alias("filas"), F.countDistinct("Id").alias("ids_distintos"), F.sum(F.col("Id").isNull().cast("long")).alias("id_nulo")))
for field, name in [("LocationId", "locations"), ("RevenueCenterId", "revenue_centers")]:
    orphaned = checks.filter(F.col(field).isNotNull()).join(dimensions[name].select(F.col("Id").alias(field)).distinct(), field, "left_anti")
    print("Tickets sin referencia:", field)
    display(orphaned.agg(F.count("*").alias("tickets"), F.countDistinct(field).alias("ids_sin_referencia")))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Tendencias y descuentos
# MAGIC Graficar tickets y proporción con descuento por día. Las tasas incluyen todos los tickets observados y no excluyen registros con Voids. Los importes de pagos son valores originales, no una definición validada de ventas.

# COMMAND ----------
def metrics(df, columns):
    return df.groupBy(*columns).agg(
        F.count("*").alias("tickets"), F.sum(F.col("has_discount").cast("long")).alias("tickets_con_descuento"),
        F.avg(F.col("has_discount").cast("double")).alias("proporcion_con_descuento"),
        F.avg("gratuity_raw").alias("propina_promedio_signo_original"),
        F.expr("percentile_approx(gratuity_raw, 0.5)").alias("propina_mediana_signo_original"),
        F.sum("check_discount_amount_raw").alias("importe_descuentos_ticket_original"),
        F.sum("item_discount_amount_raw").alias("importe_descuentos_items_original"))
daily = metrics(checks, ["business_date"]).orderBy("business_date")
by_location = metrics(checks, ["LocationId"]).orderBy(F.desc("tickets"))
by_channel = metrics(checks, ["RevenueCenterId"]).orderBy(F.desc("tickets"))
display(daily)
display(by_location)
display(by_channel)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 5. Propinas: distribución y comparación
# MAGIC Se conserva el signo. Comparar grupos dentro de la misma sucursal y canal. Son asociaciones descriptivas, sin causalidad ni porcentaje de propina definitivo. El promedio por ticket incluye tickets sin pagos; revisar su peso en calidad.

# COMMAND ----------
display(checks.agg(
    F.sum((F.col("gratuity_raw") < 0).cast("long")).alias("tickets_propina_negativa"),
    F.sum((F.col("gratuity_raw") == 0).cast("long")).alias("tickets_propina_cero"),
    F.sum((F.col("gratuity_raw") > 0).cast("long")).alias("tickets_propina_positiva"),
    F.expr("percentile_approx(gratuity_raw, array(0.01, 0.25, 0.5, 0.75, 0.99))").alias("percentiles_1_25_50_75_99")))
display(metrics(checks.filter(F.col("payment_count") > 0), ["has_discount"]).orderBy("has_discount"))
display(metrics(checks.filter(F.col("payment_count") > 0), ["LocationId", "RevenueCenterId", "has_discount"]).orderBy(F.desc("tickets")))
display(checks.groupBy("payment_count").count().orderBy("payment_count"))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 6. Catálogo observado de descuentos
# MAGIC Se mantienen separados los niveles ticket/producto. Los nombres observados no constituyen un catálogo oficial. EmployeeId identifica la acción registrada; su rol está pendiente de confirmación.

# COMMAND ----------
def discount_events(level):
    source = raw.select("business_date", "LocationId", F.col("Id").alias("check_id"))
    if level == "ticket":
        source = raw.select("business_date", "LocationId", F.col("Id").alias("check_id"), F.explode("Discounts").alias("discount"))
    else:
        items = raw.select("business_date", "LocationId", F.col("Id").alias("check_id"), F.explode("ItemsSold").alias("item"))
        source = items.select("business_date", "LocationId", "check_id", F.explode("item.Discounts").alias("discount"))
    return source.select("business_date", "LocationId", "check_id", "discount.*").withColumn("discount_level", F.lit(level))
events = discount_events("ticket").unionByName(discount_events("item"), allowMissingColumns=True)
catalog = events.groupBy("discount_level", "DiscountId", "DiscountName").agg(F.count("*").alias("eventos"), F.sum("Amount").alias("importe_original")).orderBy(F.desc("eventos"))
display(catalog)
# Actividad por ID de quien aparece en descuentos, sin atribuirle el rol de mesero.
display(events.groupBy("discount_level", "LocationId", "EmployeeId").agg(F.count("*").alias("eventos_descuento"), F.countDistinct(F.struct("business_date", "LocationId", "check_id")).alias("tickets_con_evento")).orderBy(F.desc("eventos_descuento")).limit(50))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 7. Resultados para presentar
# MAGIC Completar después de ejecutar; no inventar cifras:
# MAGIC - Cobertura observada frente a archivos y fechas esperados.
# MAGIC - Tres hallazgos con cifra, gráfico, interpretación y limitación.
# MAGIC - Calidad: duplicados, fechas y referencias.
# MAGIC - Diferencias de descuentos/propinas controlando sucursal y canal.
# MAGIC - Preguntas pendientes: roles de EmployeeId, catálogo de descuentos, fórmula de ventas y porcentaje de propina.
# MAGIC - No convertir concentración de eventos de un empleado en tasa sin denominador válido.

# COMMAND ----------
# Validar todos los destinos antes de escribir. Si una ejecución quedó parcial,
# iniciar otra desde la configuración; no reutilizar RUN para anexar duplicados.
summaries = {"coverage": coverage, "daily": daily, "by_location": by_location, "by_channel": by_channel, "discount_catalog": catalog}
assert all(not spark.catalog.tableExists(OUTPUT + "." + name + "_" + RUN) for name in summaries), "Iniciar una ejecución nueva: ya existe un destino."
for name, result in summaries.items():
    target = OUTPUT + "." + name + "_" + RUN
    result.write.format("delta").mode("append").saveAsTable(target)
    print(target)
print("Resultados guardados. Conservar este notebook con outputs para la presentación.")
