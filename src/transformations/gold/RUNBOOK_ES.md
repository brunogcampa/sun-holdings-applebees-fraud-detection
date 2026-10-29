# Guía de ejecución: segundo entregable

## 1. Conectar o actualizar el repositorio en Databricks

En Workspace, crea una carpeta Git con el repositorio
`https://github.com/brunogcampa/sun-holdings-applebees-fraud-detection` y selecciona
`main`. Si ya existe, actualízala mediante Pull. El repositorio es privado: usa tu
conexión autorizada de GitHub en Databricks. No pegues contraseñas o tokens en el código.
Si la conexión pide permisos nuevos, revísalos y complétala personalmente.

Si prefieres trabajar sin conexión Git, importa **individualmente** los tres
archivos de transformación y `validate_pipeline.ipynb` conservando su contenido.
No uses un ZIP de workspace genérico para importarlos: ya dio problemas en Week 4.

## 2. Confirmar la fuente y crear el destino separado

El volumen esperado contiene `dimensions/` y `facts/checks/` bajo:
`/Volumes/workspace/applebees_raw/source/applebees_source`.

Ejecuta esta celda SQL en un notebook con tu usuario:

```sql
CREATE SCHEMA IF NOT EXISTS workspace.applebees_phase2;
```

No reemplaces tablas de `workspace.applebees_eda`. El esquema nuevo permite
comparar la segunda entrega con los resultados históricos.

## 3. Preparar los JSON para el límite de memoria de Serverless

La primera ejecución real falló con `SparkOutOfMemoryError` en `SimdJsonReader`.
Las demás tablas se omitieron por esa dependencia. El dry run había pasado: esa
validación no garantiza que los datos puedan procesarse con la memoria disponible.

Actualiza `applebees-phase2-code` mediante **Pull**. Abre, desde Workspace y fuera
del editor del pipeline, `src/transformations/silver/prepare_checks_jsonl.ipynb`.
Selecciona el cómputo Serverless disponible y ejecuta **Run all**. El widget
`source_root` debe conservar `/Volumes/workspace/applebees_raw/source/applebees_source`.

El notebook procesa un ticket por vez, conserva los JSON originales y escribe
copias JSON Lines en `applebees_source_jsonl`, dentro del mismo volumen. Cada
archivo apunta a 16 MiB; un ticket excepcionalmente grande se mantiene completo
hasta el límite documentado de 32 MiB de texto por registro. Conserva las rutas
originales mediante `_source_file`, el orden de arrays, signos y valores numéricos.
Los manifiestos guardan hashes SHA256, conteos y la lista exacta de archivos activos.

La fotografía original debe terminar con **READY: 2,142,846 checks from 115 source files**.
Si falla, conserva el mensaje y no ejecutes el pipeline. Si pasa, continúa abajo.
No añadas este notebook como biblioteca del pipeline: es un paso previo del job.
No ejecutes preparación y pipeline al mismo tiempo. No se requiere una cuarta
clave de configuración: el código deriva la ruta preparada de `applebees.source_root`.

## 4. Crear y configurar el pipeline Lakeflow

En Jobs & Pipelines crea un pipeline ETL/Lakeflow. La denominación exacta de los
botones puede variar en la interfaz. Usa nombre `applebees-phase2-dev`, ejecución
Triggered, catálogo `workspace`, esquema `applebees_phase2` y serverless.
Las expectativas necesitan la edición/capacidad Advanced del pipeline. Comprueba
su disponibilidad en tu Free Edition antes de ejecutar.

Añade únicamente estas tres bibliotecas del repositorio:

1. `src/transformations/silver/mv_checks_cleaned.py`
2. `src/transformations/gold/mv_executive_kpis.sql`
3. `src/transformations/gold/mv_quality_metrics.sql`

Configura estos parámetros como cadenas de texto:

| Clave | Valor |
|---|---|
| `applebees.source_root` | `/Volumes/workspace/applebees_raw/source/applebees_source` |
| `applebees.start_date` | `2026-04-28` |
| `applebees.end_date` | `2026-08-20` |

Valida el pipeline. Si hay un error, conserva el texto completo, la biblioteca y
la línea que indique. No borres tablas o fuentes para intentar resolverlo.

## 5. Ejecutar una actualización manual

Inicia una actualización normal y espera su terminación. Guarda una captura del
grafo completo y el identificador de la actualización. Comprueba la pestaña de
calidad/expectations. Un error del pipeline todavía no es una ejecución exitosa.

Ejecuta las primeras consultas de `demo_queries.sql`, sustituyendo el esquema si
cambiaste el destino. Esperamos 2,142,846 checks, 127 locations, 115 días,
268,590 checks descontados, 240,699 eventos de ticket y 275,991 de producto.
Investiga cualquier diferencia: no fuerces las cifras modificando datos.

## 6. Ejecutar el validador

Abre `validate_pipeline.ipynb` y ejecuta todas sus celdas. Sus widgets deben ser:
`catalog=workspace`, `schema=applebees_phase2`, `run_id=manual`,
`validate_original_snapshot=true`.

Conservar `true` solo aplica a esta fotografía original. Para nuevas fuentes,
documenta el cambio y actualiza el contrato antes de cambiar ese indicador.

El resultado debe indicar `PASSED`. La tabla `pipeline_validation_runs` registra
cada comprobación. La primera ejecución muestra `FIRST_RUN` para la prueba de
repetición, porque todavía no existe una segunda corrida comparable.

## 7. Crear y probar el job completo

Crea un job con tres tareas, reflejando `resources/jobs/daily_orchestration_job.yml`:

1. `prepare_sources`: tipo Notebook, selecciona `prepare_checks_jsonl.ipynb` en Silver.
   Usa Serverless y pasa `source_root` con la ruta original del volumen.
2. `refresh_pipeline`: tipo Pipeline, selecciona el pipeline recién creado y exige
   éxito de `prepare_sources`.
3. `validate_outputs`: tipo Notebook, selecciona `validate_pipeline.ipynb`, con
   dependencia de éxito de `refresh_pipeline`. Usa serverless disponible y pasa
   `run_id={{job.run_id}}`, catálogo y esquema. No añadas un cluster inexistente.

Concurrencia máxima: 1. Reintento del pipeline: uno tras 60 segundos. Validador:
sin reintento automático. Horario propuesto: diario a las 07:00 de Ciudad de
México, **pausado** hasta terminar las pruebas y decidir si hay nuevas fuentes.

Ejecuta el job manualmente. Después repítelo sin cambiar fuentes ni parámetros.
Confirma `same_source_rerun_consistency` con `passed=true` y `run_complete=true`.
Registra ambos run IDs, estados y duración observada. No inventes esas duraciones.

## 8. Capturar las evidencias para la rúbrica

Guarda en Databricks o en la carpeta privada de entrega:

- Grafo Lakeflow completo con estado de la actualización.
- Job con sus tres tareas y dependencias visibles.
- Dos ejecuciones exitosas, con sus IDs y duración.
- Expectativas de calidad, cuarentena y cobertura.
- Resultados de reconciliación y prueba de repetición del validador.
- Tablas/gráficas Gold usadas en la presentación y consulta que las genera.
- Configuración de clustering y perfil de consulta si vas a afirmar mejoras de rendimiento.

No publiques datos detallados de tickets, empleados o managers en GitHub. Las
capturas deben ocultar datos personales y conservar contexto técnico suficiente.

## 9. Ensayar cinco minutos en inglés

Usa las ocho diapositivas principales y el guion. El apéndice sirve para preguntas.
Antes de presentar, actualiza el estado de ejecución: mientras no exista una
ejecución verificable, di que el pipeline está implementado y pendiente de
validación en Databricks. El análisis histórico sí tiene evidencia independiente.

## Cómo resolver fallos

| Fallo | Acción |
|---|---|
| Permiso o fuente no encontrada | Verifica volumen, ruta y acceso con tu usuario |
| JSON corrupto o tipo incorrecto | Revisa archivo de origen y razón registrada; conserva el original |
| Dimensión con ID nulo/duplicado | Corrige o aclara la referencia antes de publicar |
| Checks en cuarentena | Consulta razones y clave/archivo en privado; el gate queda fallido hasta revisión |
| Totales distintos del EDA | Revisa período, fotografía fuente y registros excluidos; compara poblaciones |
| Photon sin memoria al leer JSON | Ejecuta la preparación JSONL y actualiza las bibliotecas desde Git; no repitas la misma lectura de arrays grandes |
| Fallo transitorio de cómputo | Reintento acotado y revisión del historial del job |
| Mismo input, distinto output | Mantén horario pausado e investiga código, parámetros y determinismo |

La consola de Databricks bloquea el control automatizado del navegador en este
entorno. Estos pasos de despliegue requieren operación manual o una integración
MCP autorizada. Ninguna captura del repositorio sustituye evidencia de ejecución.
