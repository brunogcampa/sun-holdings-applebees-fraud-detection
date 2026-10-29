> Historical Week 4 document. Current Phase 2 instructions and execution status are in the root README.

# Capa de calidad — Week 4

| Control | Evidencia observada | Decisión / limitación |
|---|---|---|
| Completitud global | 115 archivos de hechos, 115 fechas; 2,142,846 tickets | Sin días globales ausentes. Falta validar sucursal × día frente a calendario operativo. |
| Clave compuesta | 0 duplicados y 0 filas excedentes | Usar fecha + sucursal + Id; no deduplicar arbitrariamente. |
| IDs y fecha | 0 IDs de ticket/sucursal nulos; 0 fechas nulas o inválidas | No confirma validez semántica de todos los IDs. |
| Coherencia temporal | 0 cierres anteriores a apertura | No certifica zona horaria ni duración esperada. |
| Referencias no nulas | 0 tickets huérfanos de sucursal y RevenueCenterId | Falta revisar referencias de empleados y productos anidados. |
| Dimensiones | IDs únicos y no nulos: locations 185, revenue_centers 23, items 16,697, employees 156,975 | 127 sucursales tienen tickets; no todas las filas de dimensiones son activas en este período. |
| Pagos vacíos | 3,856 tickets (0.18%) | Preservar, documentar y reconciliar con POS; no clasificarlos como impagos reales. |
| Propinas positivas | 3 tickets; Id=−1 en los tres | Investigar el origen; no corregir ni eliminar por signo. Evidencia individual fuera de GitHub. |
| Signo de propina | Predominan cero y negativos | Preservar signo original; usar magnitud sólo en análisis explícitamente etiquetado. |
| Catálogo y roles | Definiciones y permisos internos no confirmados | EmployeeId de pago no demuestra rol de mesero; nombre MANAGER no acredita autorización. |

## Validación del código entregado

El EDA original se ejecutó en Databricks Free Edition. La versión de código del repositorio incorpora las correcciones posteriores: comparación de propinas excluyendo pagos vacíos y escritura de tablas nuevas con comprobación previa de existencia, seguida de `append`, para evitar `errorifexists` no soportado. No se sobrescriben tablas. Una ejecución parcial debe reiniciarse desde la configuración para obtener otro RUN. El prefijo de tabla usa microsegundos; el proceso se ejecuta de forma serial, sin garantía de exclusión mutua entre sesiones.

Se verificó sintaxis Python por celda, estructura IPYNB, ausencia de outputs en notebooks de importación, reconciliación de los CSV diarios y por sucursal y denominadores de descuentos. Las correcciones publicadas no se han vuelto a ejecutar en Spark desde esta sesión; ejecutar los notebooks en orden en Databricks antes de sustituir evidencia anterior. No se afirma despliegue automático, incrementalidad ni precisión de detección.

## Problemas pendientes

Completitud de campos anidados; reconciliación contable de pagos/descuentos; moneda; roles y matriz de autorizaciones; catálogo oficial; calendario por sucursal; comparación ajustada por importe, canal y promociones; evaluación de falsos positivos. La exportación por empleado era un top 50, no el universo completo.
