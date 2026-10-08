# Metodología y trazabilidad del EDA

## Unidad y transformaciones

- Unidad principal: ticket. Clave candidata validada sin duplicados en el período: `BusinessDate + LocationId + Id`. `Id` solo no identifica una operación y `-1` no es nulo.
- Lectura de arreglos JSON completos con `multiLine=true`, modo `FAILFAST` y conservación de `source_file`.
- Pagos, productos y descuentos se agregan de forma independiente. Expandir varias listas simultáneamente produciría multiplicación de filas.
- Propina del ticket: suma de `Payments[].Gratuity` conservando el signo. Una lista vacía genera cero bajo la fórmula; no prueba que un cliente no haya dejado propina. Los importes nulos tratados como cero requieren revisar completitud anidada.
- Ticket con descuento: existe al menos un evento en `Discounts` o en `ItemsSold[].Discounts`. Se cuentan tickets únicos, no eventos.
- Descuento de ticket y producto: importes y número de eventos separados. Su posible solapamiento no está reconciliado.
- Las comparaciones con/sin descuento usan tickets con al menos un registro de pago. Los resúmenes generales incluyen todos los tickets.

## Porcentajes que no deben confundirse

| Métrica | Fórmula | Resultado |
|---|---|---:|
| Proporción global | Tickets con descuento / todos los tickets × 100 | 12.5343% |
| Promedio diario | Media aritmética del porcentaje de cada día | 12.6161% |
| Promedio por sucursal | Media aritmética del porcentaje de cada sucursal | 12.5964% |
| Participación de código de producto | Eventos del código / 275,991 eventos de producto × 100 | TASTE: 21.4145% |
| Participación de sucursal dentro de código | Eventos de la sucursal y código / eventos globales de ese código × 100 | TASTE, sucursal 155: 3.2283% |

Cada día y cada sucursal pesan igual en sus respectivos promedios. La proporción global da más peso a los grupos con mayor volumen.

## Signo y magnitud de propinas

Se preserva `gratuity_raw` para trazabilidad. Para hablar de una propina monetaria mayor se usa `abs(gratuity_raw)`: una propina de −4 tiene mayor magnitud que una de −3. Media de magnitud: 4.122923; mediana: 0. Hay 830,130 tickets (38.7396%) por encima de la media de magnitud y 1,029,265 (48.0326%) por encima de su mediana. Son importes por ticket, no tasas sobre ventas; la moneda requiere confirmación.

## Outliers

IQR = percentil 75 − percentil 25: distancia que abarca la mitad central de los datos. Con cuantiles aproximados Q1=−7 y Q3=0, IQR=7. Los límites exploratorios Q1−1.5×IQR y Q3+1.5×IQR son −17.5 y 10.5. Se observaron 77,856 tickets por debajo del límite inferior y ninguno por encima del superior. Los tres casos positivos son excepciones de signo, no outliers superiores por esta regla. Validar contexto, importe y canal antes de generar alertas. [Referencia NIST](https://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm).

## Pagos y trazabilidad

`Payments.Amount` no es una definición validada de ingreso neto. Sus signos se reportan por separado; no se ha confirmado si incluye propina. Los 57 registros de un caso corresponden a 56 líneas GC Sold por −1,145 y una CASH por +1,145, con saldo y propina cero. No equivalen a 57 cobros al cliente.

Evidencia de ejecución: tablas `eda_checks_20261007_184620_781588` y resúmenes `coverage`, `daily`, `by_location`, `by_channel` con sufijo `20261008_004407_666492` en `workspace.applebees_eda`. Los CSV agregados y verificaciones locales complementan la ejecución. El notebook con outputs y las excepciones individuales se mantienen en la entrega privada.
