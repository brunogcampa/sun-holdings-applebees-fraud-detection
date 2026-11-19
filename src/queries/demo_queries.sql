-- Run individually in a SQL notebook, after a successful pipeline update.
USE CATALOG workspace;
USE SCHEMA applebees_phase2;

SELECT * FROM gold_data_quality;
SELECT * FROM gold_coverage;
SELECT * FROM gold_quality_issues ORDER BY affected_rows DESC;
SELECT * FROM gold_missing_dates ORDER BY business_date;
SELECT * FROM gold_duplicate_keys;
SELECT * FROM pipeline_validation_runs ORDER BY recorded_at DESC,metric;

-- Daily trend: X = business_date; Y = discounted_ticket_pct, no extra SUM across dates.
SELECT * FROM gold_daily_metrics ORDER BY business_date;

-- Location comparison: denominator = that location's checks.
SELECT * FROM gold_location_metrics ORDER BY discounted_ticket_pct DESC,LocationId LIMIT 15;

-- Denominator = ALL checks lacking payment records, with separate local rate.
SELECT * FROM gold_missing_payment_locations ORDER BY empty_payment_lists DESC,LocationId LIMIT 3;

SELECT * FROM gold_tip_distribution ORDER BY tip_sign;
SELECT * FROM gold_tip_statistics;
SELECT * FROM gold_tip_comparison ORDER BY has_discount;
SELECT * FROM gold_channel_metrics ORDER BY tickets DESC;

SELECT * FROM gold_discount_catalog WHERE discount_level='item' ORDER BY events DESC;
SELECT * FROM gold_discount_location_top5 WHERE discount_level='item'
AND DiscountName IN ('TASTE','GST CORECT','SERVERERR','KITCHNERR','WALKOUT','TEMP')
ORDER BY DiscountName,ranking;

-- Private operational investigation, not public slides or CSV exports.
SELECT * FROM gold_positive_tip_evidence ORDER BY business_date,LocationId,check_id,payment_position;
SELECT * FROM gold_tip_outliers ORDER BY abs(gratuity_raw) DESC LIMIT 20;
SELECT * FROM gold_employee_discount_activity ORDER BY events DESC,EmployeeId,LocationId LIMIT 5;
SELECT * FROM gold_manager_discount_activity ORDER BY events DESC,ManagerId,LocationId LIMIT 5;
