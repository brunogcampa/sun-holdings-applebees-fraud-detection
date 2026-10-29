CREATE OR REFRESH MATERIALIZED VIEW gold_data_quality AS
SELECT count(*) AS assessed_rows,
 count_if(in_scope AND array_size(quality_reasons)=0) AS published_rows,
 count_if(array_size(quality_reasons)>0) AS quarantined_rows,
 count_if(NOT in_scope AND array_size(quality_reasons)=0) AS out_of_scope_rows,
 count_if(_corrupt_record IS NOT NULL) AS corrupt_records,
 count_if(check_id IS NULL) AS missing_check_ids,
 count_if(LocationId IS NULL) AS missing_location_ids,
 count_if(business_date IS NULL) AS invalid_dates,
 count_if(key_count > 1) AS rows_with_duplicate_keys,
 count_if(payments_null) AS null_payment_lists,
 count_if(NOT payments_null AND payment_count=0) AS empty_payment_lists,
 count_if(payment_numeric_nulls>0) AS invalid_payment_numerics,
 count_if(discount_numeric_nulls>0) AS invalid_discount_numerics,
 count_if(location_ref_valid IS NULL) AS unknown_locations,
 count_if(channel_ref_valid IS NULL) AS unknown_channels,
 count_if(open_time IS NULL) AS invalid_open_times,
 count_if(close_time IS NULL) AS invalid_close_times,
 count_if(close_time < open_time) AS close_before_open
FROM silver_checks_assessed;

CREATE OR REFRESH MATERIALIZED VIEW gold_quality_issues AS
SELECT reason, count(*) AS affected_rows FROM (
 SELECT explode(quality_reasons) AS reason FROM silver_checks_assessed
) GROUP BY reason;

CREATE OR REFRESH MATERIALIZED VIEW gold_duplicate_keys AS
SELECT business_date, LocationId, check_id, count(*) AS rows_per_key
FROM silver_checks_assessed
WHERE business_date IS NOT NULL AND LocationId IS NOT NULL AND check_id IS NOT NULL
GROUP BY business_date, LocationId, check_id HAVING count(*)>1;

CREATE OR REFRESH MATERIALIZED VIEW gold_missing_dates AS
SELECT expected.business_date FROM (
 SELECT explode(sequence(to_date('${applebees.start_date}'),to_date('${applebees.end_date}'))) AS business_date
) expected LEFT ANTI JOIN (SELECT DISTINCT business_date FROM silver_checks) actual
ON expected.business_date=actual.business_date;
