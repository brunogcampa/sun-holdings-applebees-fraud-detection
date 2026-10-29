> Historical Week 4 document. Current Phase 2 instructions and execution status are in the root README.

# Resultados agregados Week 4

| Archivo | Granularidad / denominador |
|---|---|
| eda_por_fecha.csv | Una fecha; proporcion_con_descuento es fracción 0–1 |
| eda_por_sucursal.csv | Una LocationId; proporcion_con_descuento es fracción 0–1 |
| eda_por_canal.csv | Un RevenueCenterId; proporcion_con_descuento es fracción 0–1 |
| top5_sucursales_por_descuento.csv | Nivel + ID de descuento + sucursal; porcentaje_eventos_categoria usa eventos de ese código |
| sucursales_repetidas_top5_descuentos.csv | Sucursal y recurrencia en rankings de categorías |
| tickets_sin_pago_por_sucursal.csv | Sucursal; revisar encabezados para porcentaje del total de casos o de tickets locales |
| pagos_por_canal.csv | Canal; importes positivos y negativos separados, sin definición contable de ingreso neto |
| catalogo_descuentos.csv | 106 IDs; interpretación por nombre, no catálogo oficial |

No contienen detalles por ticket ni identificadores de empleados. Las cifras corresponden al período 28 de abril–20 de agosto de 2026. Los CSV originales completos y evidencia individual se conservan fuera del repositorio. No mezclar fracciones 0–1 y porcentajes 0–100 en visualizaciones. Ver [metodología](historical_docs_metodologia.md).
