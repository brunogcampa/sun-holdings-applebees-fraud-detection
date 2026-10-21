# Transformaciones

- `silver/`: lectura y estandarización de checks, signos originales, trazabilidad y expansión separada de descuentos.
- `gold/`: vistas materializadas de métricas diarias, por location, catálogo y calidad.
- `gold/queries/`: consultas exploratorias del EDA histórico. Son SELECT para ejecución individual y no están incluidas como bibliotecas del pipeline.

Los archivos Python con decoradores `pyspark.pipelines` se ejecutan dentro de
Lakeflow, no como scripts Python locales. No contienen escrituras ni acciones
de Spark dentro de las definiciones de datasets. Las reglas de calidad registran
incumplimientos sin eliminar automáticamente registros.
