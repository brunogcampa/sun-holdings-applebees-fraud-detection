> Historical Week 4 document. Current Phase 2 instructions and execution status are in the root README.

# Consultas SQL del EDA

Primero validar en Databricks; después versionar el código validado en GitHub.
Estos archivos fueron preparados localmente y aún no ejecutados en Databricks.

1. Ejecutar la primera celda de `01_eda_checks.sql`: publica `checks_current`
   sobre la tabla histórica conocida. Confirmar que esa tabla exista.
2. Ejecutar sus SELECT individualmente, en un notebook SQL. La cobertura esperada
   es 2,142,846 tickets, 127 locations, 115 días, 2026-04-28 a 2026-08-20.
3. Importar y ejecutar `../../../../notebooks/02_publish_discount_events.py` para publicar
   los eventos detallados. En el período original se observaron 240,699 eventos
   a nivel ticket y 275,991 a nivel producto. Si difieren, investigar antes de usar.
4. Ejecutar `02_discount_events.sql` para categorías, locations, managers y empleados.
5. Conservar notebook con resultados en Databricks y documentar tabla fuente,
   fecha de ejecución, filtros y discrepancias antes de publicar código en GitHub.

Los SELECT no modifican datos. Las vistas `*_current` cambian la fuente visible
para futuras consultas; las tablas históricas se conservan. Cada publicación de
eventos relee el período completo: esta primera versión no es incremental.

Los porcentajes diarios, por location y globales tienen denominadores diferentes.
Propina por ticket = suma de `Payments[].Gratuity`; comparar magnitudes con `abs`.
Pagos conservan su signo original y no se etiquetan como ventas netas o ingresos
sin reconciliación. No sumar importes de descuentos de ambos niveles sin validar
si se solapan. Los outliers IQR son señales exploratorias, no evidencia de fraude.

En GitHub se guarda código y documentación; los resultados con IDs de empleados,
managers o tickets se conservan en el entorno privado.

