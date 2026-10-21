-- Global daily denominator = all observed checks on that date.
CREATE OR REFRESH MATERIALIZED VIEW gold_daily_metrics AS
SELECT business_date, count(*) AS tickets, count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS discounted_ticket_pct,
 avg(abs(gratuity_raw)) AS mean_tip_magnitude,
 sum(payment_amount_raw) AS payment_amount_signed
FROM silver_checks WHERE business_date IS NOT NULL GROUP BY business_date;
