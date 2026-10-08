# EDA Week 4: hallazgos y decisiones

## Problema de negocio

Priorizar la revisión de descuentos y propinas que requieren explicación operativa, sin asumir que una excepción es fraude. El EDA establece una línea base y separa problemas de datos, promociones legítimas e hipótesis de revisión.

## Cobertura y calidad

2,142,846 tickets, 127 sucursales, 115 días (2026-04-28 a 2026-08-20). Los controles globales de claves, fechas y referencias de sucursal/canal no detectaron duplicados ni huérfanos. [Calidad y límites](data_quality.md).

## Descuentos y evolución

268,590 tickets tienen algún descuento (12.5343% global). El promedio diario es 12.6161%; el promedio por sucursal es 12.5964%. Son tres preguntas y denominadores distintos. La sucursal 196 encabeza el porcentaje de tickets con descuento con 20.3341%; esto no equivale a mayor número absoluto de descuentos ni prueba abuso. Revisar canal, campañas y volumen antes de comparar desempeño.

El descuento promedio por evento es aproximadamente 8.11 a nivel ticket y 3.88 a nivel producto, en unidades monetarias de origen. Son medias de eventos, no descuentos promedio por todos los tickets. No sumar ambos niveles sin reconciliar solapamiento.

## Tipos y concentración

| Código de producto | Eventos | % de 275,991 eventos |
|---|---:|---:|
| TASTE | 59,102 | 21.41% |
| GST CORECT | 50,022 | 18.12% |
| SERVERERR | 35,518 | 12.87% |
| KITCHNERR | 35,410 | 12.83% |
| WALKOUT | 27,306 | 9.89% |
| TEMP | 20,853 | 7.56% |

La sucursal 174 aparece en el top 5 de cuatro de estas seis categorías; las sucursales 155 y 168 aparecen en tres. Para TASTE, la sucursal 155 realiza 3.23% de los eventos de esa categoría. Para GST CORECT, la sucursal 174 realiza 4.40%. No son porcentajes sobre tickets de la sucursal. Confirmar catálogo y causas antes de concluir incumplimiento. [Tabla completa y fórmulas](../reports/week4/README.md).

## Propinas

1,029,262 tickets con propina agregada negativa, 1,113,581 con cero y 3 con positiva. El signo negativo es habitual en este dataset. La comparación con registros de pago muestra medias originales de −4.2691 sin descuento y −3.1548 con descuento. La asociación no prueba causalidad y puede reflejar canales o tipos de operación diferentes. La media de magnitud sobre todo el universo es 4.122923 y la mediana 0. [Transformaciones y outliers](metodologia.md).

## Tickets sin registros de pago

3,856 casos (0.18%). Los tres principales grupos concentran 71.08% de los casos:

| Sucursal | Casos | % de los 3,856 casos | % de tickets de la sucursal |
|---|---:|---:|---:|
| 87 — Warsaw | 1,335 | 34.62% | 4.56% |
| 1 — Topeka | 928 | 24.07% | 3.42% |
| 141 — Prescott | 478 | 12.40% | 3.61% |

Una lista Payments vacía significa ausencia de registros de pago en ese campo, no prueba de falta de cobro. Es una prioridad de reconciliación con POS y revisión de la extracción.

## Recomendaciones

1. Reconciliar pagos vacíos en las sucursales 87, 1 y 141 con POS y responsables de extracción.
2. Confirmar las reglas y autorizaciones de descuentos, empezando por categorías frecuentes y sucursales recurrentes.
3. Comparar tasas dentro de contextos equivalentes: canal, volumen, importe y campaña. Evitar rankings de empleados sin denominador.
4. Validar casos extremos antes de diseñar alertas y medir falsos positivos. Una lista larga de pagos puede representar registros compensatorios.
5. Convertir el análisis por lote en ingestión incremental y dashboard de revisión cuando las reglas estén confirmadas.

Impacto esperado: reducir el universo de revisión y mejorar la trazabilidad. No se ha medido ahorro ni eficacia de un modelo de fraude.
