-- Pipeline libraries: Lakeflow resolves these dependencies from the dataset names.
-- The Gold population contains valid, in-scope checks only. Raw/quarantine counts remain visible.
CREATE OR REFRESH MATERIALIZED VIEW gold_coverage AS
SELECT count(*) AS tickets, count(DISTINCT LocationId) AS locations,
 count(DISTINCT business_date) AS observed_days, min(business_date) AS start_date, max(business_date) AS end_date,
 count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / nullif(count(*),0) AS global_discounted_ticket_pct,
 count_if(payment_count = 0) AS empty_payment_lists,
 count_if(payments_null) AS null_payment_lists,
 count_if(tip_available) AS tickets_with_tip_data
FROM silver_checks;

CREATE OR REFRESH MATERIALIZED VIEW gold_daily_metrics AS
SELECT business_date, count(*) AS tickets, count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS discounted_ticket_pct,
 avg(abs(gratuity_raw)) AS mean_tip_magnitude_legacy_all_checks,
 avg(CASE WHEN tip_available THEN abs(gratuity_raw) END) AS mean_tip_magnitude_available
FROM silver_checks GROUP BY business_date;

CREATE OR REFRESH MATERIALIZED VIEW gold_location_metrics AS
SELECT LocationId, location_name, count(*) AS tickets, count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS discounted_ticket_pct,
 count_if(payment_count = 0) AS empty_payment_lists,
 100.0 * count_if(payment_count = 0) / count(*) AS empty_payment_pct_within_location
FROM silver_checks GROUP BY LocationId, location_name;

CREATE OR REFRESH MATERIALIZED VIEW gold_channel_metrics AS
SELECT RevenueCenterId, channel_name, count(*) AS tickets,
 sum(payment_amount_raw) AS payment_amount_signed,
 sum(gratuity_raw) AS tip_amount_signed,
 count_if(has_discount) AS discounted_tickets,
 100.0 * count_if(has_discount) / count(*) AS discounted_ticket_pct
FROM silver_checks GROUP BY RevenueCenterId, channel_name;

CREATE OR REFRESH MATERIALIZED VIEW gold_tip_distribution AS
SELECT CASE WHEN gratuity_raw < 0 THEN 'negative' WHEN gratuity_raw > 0 THEN 'positive' ELSE 'zero' END AS tip_sign,
 count(*) AS tickets, 100.0 * count(*) / sum(count(*)) OVER () AS pct_of_all_checks,
 count_if(NOT tip_available) AS tickets_without_observed_tip_data
FROM silver_checks GROUP BY CASE WHEN gratuity_raw < 0 THEN 'negative' WHEN gratuity_raw > 0 THEN 'positive' ELSE 'zero' END;

CREATE OR REFRESH MATERIALIZED VIEW gold_tip_statistics AS
WITH stats AS (
 SELECT avg(abs(gratuity_raw)) AS mean_tip, percentile(abs(gratuity_raw),0.5) AS median_tip FROM silver_checks
)
SELECT s.mean_tip, s.median_tip,
 100.0 * count_if(abs(c.gratuity_raw) > s.mean_tip) / count(*) AS pct_above_mean_magnitude,
 100.0 * count_if(abs(c.gratuity_raw) > s.median_tip) / count(*) AS pct_above_median_magnitude
FROM silver_checks c CROSS JOIN stats s GROUP BY s.mean_tip, s.median_tip;

CREATE OR REFRESH MATERIALIZED VIEW gold_tip_comparison AS
SELECT has_discount, count(*) AS tickets,
 avg(abs(gratuity_raw)) AS mean_tip_magnitude, percentile(abs(gratuity_raw),0.5) AS median_tip_magnitude
FROM silver_checks WHERE tip_available GROUP BY has_discount;

CREATE OR REFRESH MATERIALIZED VIEW gold_discount_catalog AS
WITH counts AS (
 SELECT discount_level, DiscountName, count(*) AS events, sum(Amount) AS amount_signed,
 avg(abs(Amount)) AS mean_amount_magnitude FROM silver_discount_events GROUP BY discount_level, DiscountName
)
SELECT *, 100.0 * events / sum(events) OVER (PARTITION BY discount_level) AS pct_of_level_events FROM counts;

CREATE OR REFRESH MATERIALIZED VIEW gold_discount_location_top5 AS
WITH counts AS (
 SELECT discount_level, DiscountName, LocationId, count(*) AS events
 FROM silver_discount_events GROUP BY discount_level, DiscountName, LocationId
), ranked AS (
 SELECT *, 100.0 * events / sum(events) OVER (PARTITION BY discount_level, DiscountName) AS pct_of_category_events,
 row_number() OVER (PARTITION BY discount_level, DiscountName ORDER BY events DESC, LocationId) AS ranking FROM counts
)
SELECT * FROM ranked WHERE ranking <= 5;

CREATE OR REFRESH MATERIALIZED VIEW gold_missing_payment_locations AS
SELECT LocationId, location_name, tickets, empty_payment_lists,
 100.0 * empty_payment_lists / nullif(sum(empty_payment_lists) OVER (),0) AS pct_of_all_missing_payment_checks,
 empty_payment_pct_within_location FROM gold_location_metrics;

CREATE OR REFRESH MATERIALIZED VIEW gold_tip_outliers AS
WITH q AS (
 SELECT percentile(abs(gratuity_raw),0.25) AS q1, percentile(abs(gratuity_raw),0.75) AS q3
 FROM silver_checks WHERE tip_available
)
SELECT c.business_date, c.LocationId, c.check_id, c.RevenueCenterId, c.gratuity_raw,
 q.q1, q.q3, q.q3-q.q1 AS iqr, q.q3+1.5*(q.q3-q.q1) AS upper_threshold, c.source_file
FROM silver_checks c CROSS JOIN q
WHERE c.tip_available AND abs(c.gratuity_raw) > q.q3+1.5*(q.q3-q.q1);

CREATE OR REFRESH MATERIALIZED VIEW gold_positive_tip_evidence AS
SELECT p.* FROM silver_payments p
INNER JOIN silver_checks c USING(business_date,LocationId,check_id)
WHERE c.gratuity_raw > 0;

-- IDs stay in private Databricks tables, never in exported public evidence.
CREATE OR REFRESH MATERIALIZED VIEW gold_employee_discount_activity AS
WITH counts AS (
 SELECT EmployeeId, LocationId, count(*) AS events FROM silver_discount_events GROUP BY EmployeeId, LocationId
), shares AS (
 SELECT *, 100.0*events/sum(events) OVER () AS pct_of_all_events,
 100.0*events/sum(events) OVER (PARTITION BY LocationId) AS pct_of_location_events FROM counts
)
SELECT * FROM shares WHERE EmployeeId IS NOT NULL AND EmployeeId > 0;

CREATE OR REFRESH MATERIALIZED VIEW gold_manager_discount_activity AS
WITH counts AS (
 SELECT ManagerId, LocationId, count(*) AS events FROM silver_discount_events GROUP BY ManagerId, LocationId
), shares AS (
 SELECT *,100.0*events/sum(events) OVER () AS pct_of_all_events FROM counts
)
SELECT * FROM shares WHERE ManagerId IS NOT NULL AND ManagerId > 0;
