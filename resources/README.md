# Orquestación

- `jobs/`: tareas, dependencias y programación. El job de este proyecto refresca el pipeline; su horario está **pausado**.
- `pipelines/`: configuración Lakeflow, destino, parámetros y archivos fuente.

La lógica de tablas vive en `../src/transformations/`. Estos YAML no se ejecutan
al subirlos a GitHub; falta validarlos y desplegarlos en Databricks.
