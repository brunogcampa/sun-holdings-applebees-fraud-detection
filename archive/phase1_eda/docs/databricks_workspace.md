> Historical Week 4 document. Current Phase 2 instructions and execution status are in the root README.

# Organización en Databricks

Workspace guarda el código y notebooks. Unity Catalog guarda esquemas, tablas y volúmenes. Los JSON originales están en un volumen, no en GitHub.

Carpeta de código: `Applebees_Databricks_Challenge/notebooks`. Volumen de datos: `workspace.applebees_raw.source`. Tablas del EDA: `workspace.applebees_eda`, con sufijo de ejecución UTC. La extracción mantiene `dimensions/` y `facts/`.

El notebook ejecutado es evidencia técnica. La exportación HTML transaccional se conserva en la entrega privada.
