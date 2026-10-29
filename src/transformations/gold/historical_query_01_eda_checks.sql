-- Databricks SQL. Ejecutar primero esta celda.
-- Fuente histórica conocida del EDA; confirmar que existe antes de cambiar la vista.
-- La vista apunta a una ejecución explícita, no a una tabla elegida por fecha automáticamente.
CREATE OR REPLACE VIEW workspace.applebees_eda.checks_current AS
SELECT * FROM workspace.applebees_eda.eda_checks_20261007_184620_781588;

-- Ejecutar cada SELECT por separado para conservar su resultado/gráfica.
-- 1. Cobertura y calidad.
SELECT count(*) AS tickets, count(DISTINCT LocationId) AS locations,
 count(DISTINCT business_date) AS days_observed,
 min(business_date) AS start_date, max(business_date) AS end_date,
 count_if(check_id IS NULL) AS null_check_ids,
 count_if(LocationId IS NULL) AS null_location_ids,
 count_if(business_date IS NULL) AS invalid_dates,
 count_if(payments_null) AS null_payment_lists,
 count_if(payment_count = 0 AND NOT payments_null) AS empty_payment_lists,
 count_if(close_time < open_time) AS close_before_open
FROM workspace.applebees_eda.checks_current;

-- 2. Duplicados de la clave compuesta. No eliminar automáticamente.
SELECT business_date, LocationId, check_id, count(*) AS rows_per_key
FROM workspace.applebees_eda.checks_current
WHERE business_date IS NOT NULL AND LocationId IS NOT NULL AND check_id IS NOT NULL
GROUP BY business_date, LocationId, check_id HAVING count(*) > 1;

-- 3. Fechas faltantes en el intervalo esperado.
WITH expected AS (
 SELECT explode(sequence(DATE '2026-04-28', DATE '2026-08-20')) AS business_date
)
SELECT e.business_date FROM expected e
LEFT ANTI JOIN workspace.applebees_eda.checks_current c
ON e.business_date = c.business_date ORDER BY e.business_date;

-- 4. Evolución diaria: denominador = todos los tickets de cada día.
SELECT business_date, count(*) AS tickets,
 count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS discounted_ticket_pct
FROM workspace.applebees_eda.checks_current
WHERE business_date IS NOT NULL GROUP BY business_date ORDER BY business_date;

-- 5. Tres promedios diferentes: global ponderado, día y location.
WITH daily AS (
 SELECT business_date, 100.0 * count_if(has_discount) / count(*) AS pct
 FROM workspace.applebees_eda.checks_current
 WHERE business_date IS NOT NULL GROUP BY business_date
), locations AS (
 SELECT LocationId, 100.0 * count_if(has_discount) / count(*) AS pct
 FROM workspace.applebees_eda.checks_current
 WHERE LocationId IS NOT NULL GROUP BY LocationId
)
SELECT count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS global_weighted_pct,
 (SELECT avg(pct) FROM daily) AS mean_daily_pct,
 (SELECT avg(pct) FROM locations) AS mean_location_pct
FROM workspace.applebees_eda.checks_current;

-- 6. Locations con mayor porcentaje de tickets descontados.
SELECT LocationId, count(*) AS tickets, count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS discounted_ticket_pct
FROM workspace.applebees_eda.checks_current GROUP BY LocationId
ORDER BY discounted_ticket_pct DESC, LocationId LIMIT 15;

-- 7. Top 3 sin registro de pago. Ambos denominadores quedan explícitos.
WITH locations AS (
 SELECT LocationId, count(*) AS tickets,
 count_if(payment_count = 0 AND NOT payments_null) AS missing_payment_tickets
 FROM workspace.applebees_eda.checks_current GROUP BY LocationId
)
SELECT *, 100.0 * missing_payment_tickets / sum(missing_payment_tickets) OVER ()
 AS pct_of_all_missing_payment_tickets,
 100.0 * missing_payment_tickets / tickets AS pct_of_location_tickets
FROM locations ORDER BY missing_payment_tickets DESC, LocationId LIMIT 3;

-- 8. Signo de la SUMA de Gratuity por ticket; incluye todos los tickets.
SELECT count(*) AS tickets,
 count_if(gratuity_raw = 0) AS zero_tip_tickets,
 100.0 * count_if(gratuity_raw = 0) / count(*) AS zero_tip_pct,
 count_if(gratuity_raw < 0) AS negative_tip_tickets,
 100.0 * count_if(gratuity_raw < 0) / count(*) AS negative_tip_pct,
 count_if(gratuity_raw > 0) AS positive_tip_tickets,
 100.0 * count_if(gratuity_raw > 0) / count(*) AS positive_tip_pct
FROM workspace.applebees_eda.checks_current;

-- 9. Superior significa mayor magnitud: abs(-4) > abs(-3).
WITH stats AS (
 SELECT avg(abs(gratuity_raw)) AS mean_tip,
 percentile(abs(gratuity_raw), 0.5) AS median_tip
 FROM workspace.applebees_eda.checks_current
)
SELECT s.mean_tip, s.median_tip,
 100.0 * count_if(abs(c.gratuity_raw) > s.mean_tip) / count(*) AS pct_above_mean,
 100.0 * count_if(abs(c.gratuity_raw) > s.median_tip) / count(*) AS pct_above_median
FROM workspace.applebees_eda.checks_current c CROSS JOIN stats s
GROUP BY s.mean_tip, s.median_tip;

-- 10. Comparación descriptiva: solo tickets con al menos un pago.
SELECT has_discount, count(*) AS tickets, avg(abs(gratuity_raw)) AS mean_tip_magnitude,
 percentile(abs(gratuity_raw), 0.5) AS median_tip_magnitude
FROM workspace.applebees_eda.checks_current WHERE payment_count > 0
GROUP BY has_discount ORDER BY has_discount;

-- 11. Misma comparación por location y canal. No implica causalidad.
SELECT LocationId, RevenueCenterId, has_discount, count(*) AS tickets,
 avg(abs(gratuity_raw)) AS mean_tip_magnitude
FROM workspace.applebees_eda.checks_current WHERE payment_count > 0
GROUP BY LocationId, RevenueCenterId, has_discount
ORDER BY LocationId, RevenueCenterId, has_discount;

-- 12. Pagos por canal: suma original, no una definición validada de ventas.
SELECT RevenueCenterId, count(*) AS tickets,
 sum(payment_amount_raw) AS payment_amount_signed,
 sum(gratuity_raw) AS gratuity_signed,
 sum(abs(gratuity_raw)) AS gratuity_magnitude_by_ticket
FROM workspace.applebees_eda.checks_current GROUP BY RevenueCenterId
ORDER BY tickets DESC;

-- 13. Outliers de propina: IQR = Q3 - Q1; límite superior = Q3 + 1.5 * IQR.
-- Regla exploratoria; un outlier no confirma fraude.
WITH quartiles AS (
 SELECT percentile(abs(gratuity_raw), 0.25) AS q1,
 percentile(abs(gratuity_raw), 0.75) AS q3
 FROM workspace.applebees_eda.checks_current WHERE payment_count > 0
)
SELECT c.business_date, c.LocationId, c.check_id, c.RevenueCenterId,
 c.gratuity_raw, c.payment_count, q.q1, q.q3,
 q.q3 + 1.5 * (q.q3 - q.q1) AS upper_threshold, c.source_file
FROM workspace.applebees_eda.checks_current c CROSS JOIN quartiles q
WHERE c.payment_count > 0 AND abs(c.gratuity_raw) > q.q3 + 1.5 * (q.q3 - q.q1)
ORDER BY abs(c.gratuity_raw) DESC;

-- 14. Casos de propina positiva, con trazabilidad del ticket.
-- EmployeeId de cada pago requiere la lista Payments del JSON original.
SELECT business_date, LocationId, check_id, RevenueCenterId,
 gratuity_raw, payment_count, source_file
FROM workspace.applebees_eda.checks_current WHERE gratuity_raw > 0
ORDER BY business_date, LocationId, check_id;
