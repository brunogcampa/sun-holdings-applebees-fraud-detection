# Organización en Databricks

Workspace guarda el código y notebooks. Unity Catalog guarda esquemas, tablas y volúmenes. Los JSON originales están en un volumen, no en GitHub.

Carpeta de código: `Applebees_Databricks_Challenge/notebooks`. Volumen de datos: `workspace.applebees_raw.source`. Tablas del EDA: `workspace.applebees_eda`, con sufijo de ejecución UTC. La extracción mantiene `dimensions/` y `facts/`.

El notebook ejecutado es evidencia técnica; la presentación comunica hallazgos y decisiones. Los materiales de las diapositivas 9, 10 y 11 están en [presentacion](presentacion/README.md). La exportación HTML transaccional se conserva en la entrega privada.
