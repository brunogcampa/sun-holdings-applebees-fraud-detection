# Databricks notebook source
# MAGIC %md
# MAGIC # Preparar catálogo, volumen y esquema del EDA
# MAGIC Ejecutar después de importar el paquete del workspace. Elegir un catálogo donde se tenga permiso de creación. No cambia permisos ni elimina recursos existentes.

# COMMAND ----------
display(spark.sql("SHOW CATALOGS"))
dbutils.widgets.text("catalog", "workspace", "Catálogo de trabajo")

# COMMAND ----------
catalog = dbutils.widgets.get("catalog")
assert catalog and catalog.replace("_", "").isalnum(), "Indicar un catálogo válido de la lista."
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.applebees_raw")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.applebees_eda")
spark.sql(f"CREATE VOLUME IF NOT EXISTS `{catalog}`.applebees_raw.source")
display(spark.sql(f"SHOW VOLUMES IN `{catalog}`.applebees_raw"))
print("Subir applebees_source_data.zip en:", f"/Volumes/{catalog}/applebees_raw/source/")
print("archive_path:", f"/Volumes/{catalog}/applebees_raw/source/applebees_source_data.zip")
print("data_root:", f"/Volumes/{catalog}/applebees_raw/source/applebees_source")
print("output_schema:", f"{catalog}.applebees_eda")
