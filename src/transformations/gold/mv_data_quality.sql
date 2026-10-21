CREATE OR REFRESH MATERIALIZED VIEW gold_data_quality AS
SELECT count(*) AS tickets, count(DISTINCT LocationId) AS locations,
 count(DISTINCT business_date) AS observed_days,
 min(business_date) AS start_date, max(business_date) AS end_date,
 count_if(check_id IS NULL) AS null_check_ids,
 count_if(LocationId IS NULL) AS null_location_ids,
 count_if(business_date IS NULL) AS invalid_dates,
 count_if(payments_null) AS null_payment_lists,
 count_if(payment_count = 0 AND NOT payments_null) AS empty_payment_lists,
 count_if(close_time < open_time) AS close_before_open
FROM silver_checks;

CREATE OR REFRESH MATERIALIZED VIEW gold_duplicate_keys AS
SELECT business_date, LocationId, check_id, count(*) AS rows_per_key
FROM silver_checks
WHERE business_date IS NOT NULL AND LocationId IS NOT NULL AND check_id IS NOT NULL
GROUP BY business_date, LocationId, check_id HAVING count(*) > 1;
