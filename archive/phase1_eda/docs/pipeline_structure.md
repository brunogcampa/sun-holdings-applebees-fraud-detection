> Historical Week 4 document. Current Phase 2 instructions and execution status are in the root README.

# Estructura y siguiente validación en Databricks

La organización sigue la separación solicitada: `resources/jobs` define cuándo y
en qué orden ejecutar; `resources/pipelines` configura Lakeflow; `src/transformations`
define qué datos producir. `databricks.yml` reúne los recursos y parámetros.

## Datos y tablas

Los JSON existentes del volumen son la fuente de esta primera versión batch.
`silver_checks_raw` conserva los arreglos anidados y archivo de origen;
`silver_checks` convierte fechas y agrega cada lista por separado para conservar
una fila por check. No se deduplican ni eliminan silenciosamente fechas inválidas.
`silver_discount_events` separa eventos de ticket y producto antes de unirlos.

Gold produce `gold_daily_metrics`, `gold_location_metrics`, `gold_discount_catalog`,
`gold_data_quality` y `gold_duplicate_keys`. Los porcentajes tienen denominadores
explícitos. La propina por check suma `Payments[].Gratuity`; su magnitud es el valor
absoluto de esa suma. Los pagos mantienen su signo y no se denominan ventas netas.

El destino por defecto es `workspace.applebees_pipeline_dev`, separado de
`workspace.applebees_eda`. Las consultas históricas de `gold/queries` siguen
apuntando a las tablas del EDA; no se cambian automáticamente al nuevo pipeline.

## Pasos desde la plataforma web

1. Actualizar la carpeta Git del repositorio en Databricks o importar los archivos
   de transformación. No es necesario instalar Git en la computadora para usar la interfaz web.
2. Crear/configurar un pipeline Lakeflow con los seis archivos listados en
   `resources/pipelines/lakeflow_pipeline.yml`. No agregar `gold/queries` como fuente.
3. Usar el catálogo `workspace`, esquema `applebees_pipeline_dev` y configurar
   `applebees.source_root`, `applebees.start_date` y `applebees.end_date` con los valores
   de `databricks.yml`. Confirmar disponibilidad de Lakeflow/serverless y permisos en la cuenta.
4. Validar el pipeline y ejecutar una actualización manual. Comparar cobertura,
   claves duplicadas, fechas, descuentos y propinas contra los resultados históricos.
   Referencias del período original: 2,142,846 checks, 127 locations, 115 días,
   268,590 checks descontados, 240,699 eventos de ticket y 275,991 de producto.
5. Investigar diferencias antes de cambiar la fuente de las consultas o activar
   programación. El job de ejemplo tiene horario diario de las 07:00 de Ciudad
   de México y estado **PAUSED**; no se ha creado ni activado en el workspace.

Alternativa con CLI, cuando se disponga de ella: `databricks bundle validate -t dev`,
después `databricks bundle deploy -t dev`, y ejecutar manualmente el job desplegado.
No se requiere la CLI para continuar revisando y ejecutando desde la interfaz web.

## Estado real

Reorganización y verificaciones locales de sintaxis/referencias realizadas. El
bundle, las expectativas y los SQL del nuevo pipeline aún requieren validación y
ejecución en Databricks; no se afirma que el pipeline esté desplegado ni que sea
incremental. Los notebooks del EDA ejecutado y sus importaciones se conservan.

Fuentes oficiales usadas para preparar la configuración:
- [Recursos de Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/resources).
- [Definiciones de datasets con Python](https://docs.databricks.com/aws/en/ldp/developer/definition-function).
- [Vistas materializadas con Python](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-materialized-view).
