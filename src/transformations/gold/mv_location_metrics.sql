CREATE OR REFRESH MATERIALIZED VIEW gold_location_metrics AS
SELECT LocationId, count(*) AS tickets, count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS discounted_ticket_pct,
 count_if(payment_count = 0 AND NOT payments_null) AS empty_payment_lists,
 avg(abs(gratuity_raw)) AS mean_tip_magnitude
FROM silver_checks GROUP BY LocationId;
