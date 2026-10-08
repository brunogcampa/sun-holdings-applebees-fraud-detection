# Sun Holdings × Databricks — Applebee’s

EDA de Week 4 para entender patrones de descuentos y propinas, documentar problemas de calidad y priorizar revisiones operativas. Una anomalía no constituye evidencia de fraude.

## Estado y resultados

El EDA fue ejecutado en Databricks Free Edition y contrastado con los JSON originales. Se observaron **2,142,846 tickets de 127 sucursales durante 115 días**, del **28 de abril al 20 de agosto de 2026**. La automatización incremental, el modelo de detección y el dashboard operativo siguen pendientes.

| Indicador | Resultado | Denominador |
|---|---:|---|
| Tickets con algún descuento | 268,590 · 12.5343% | Todos los tickets del período |
| Promedio diario con descuento | 12.6161% | Promedio de 115 porcentajes diarios |
| Promedio por sucursal con descuento | 12.5964% | Promedio de 127 porcentajes por sucursal |
| Tickets sin registros en Payments | 3,856 · 0.1800% | Todos los tickets |
| Propina agregada negativa / cero / positiva | 1,029,262 / 1,113,581 / 3 | Todos los tickets; los pagos vacíos producen cero bajo la agregación |
| Catálogo observado | 106 IDs · 93 nombres distintos | Conservando diferencias de mayúsculas y minúsculas |

## Entregables

- [Hallazgos, conclusiones y decisiones](docs/eda_week4.md).
- [Reglas de calidad, problemas y pendientes](docs/data_quality.md).
- [Fórmulas, denominadores y trazabilidad](docs/metodologia.md).
- [Estructura del JSON transaccional](docs/estructura_datos.md).
- [106 códigos y sus interpretaciones](docs/catalogo_descuentos.md). Las definiciones y autorizaciones internas no están confirmadas.
- [Resultados agregados](reports/week4/README.md).
- [Material de presentación](docs/presentacion/README.md): gráficas y tabla de las diapositivas 9–11.
- [Instrucciones para Databricks Free Edition](docs/carga_free_edition.md).

## Ejecución

Importar individualmente los notebooks `.ipynb` de `notebooks/import/` en `Applebees_Databricks_Challenge/notebooks`. Ejecutar `00_setup_catalog`, cargar el ZIP de datos en un volumen, ejecutar `00_extract_source_data` y después `01_eda_applebees` desde la primera celda. Los ZIP genéricos de workspace dieron problemas de importación; usar los notebooks individuales.

Ejemplo de configuración: `data_root=/Volumes/workspace/applebees_raw/source/applebees_source`, `output_schema=workspace.applebees_eda`. Cada ejecución genera tablas Delta con un sufijo UTC único. La versión de código guardada corrige la incompatibilidad de `errorifexists` observada en Free Edition; ver notas de validación en [calidad](docs/data_quality.md).

## Organización

```text
notebooks/             Código fuente Databricks y copias IPYNB sin outputs
docs/                  Metodología, calidad, hallazgos y presentación
reports/week4/         Resúmenes agregados autorizados para este repositorio
src/                   Empaquetado local de datos fuente
config/                Configuración y rutas de ejemplo
sql/                   Reservado para consultas operativas futuras
tests/                 Verificación estática de la entrega
dashboards/            Estado de visualizaciones y próximos pasos
```

Los JSON originales, ZIP de datos, dimensiones de empleados, exports HTML con detalle transaccional, credenciales y evidencia individual se conservan fuera del repositorio. No se cambian sus permisos de acceso.
