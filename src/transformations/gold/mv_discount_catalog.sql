-- Keep levels separate: their monetary meaning may overlap.
CREATE OR REFRESH MATERIALIZED VIEW gold_discount_catalog AS
SELECT discount_level, DiscountId, DiscountName, count(*) AS events,
 sum(Amount) AS amount_signed, avg(abs(Amount)) AS mean_amount_magnitude
FROM silver_discount_events GROUP BY discount_level, DiscountId, DiscountName;
