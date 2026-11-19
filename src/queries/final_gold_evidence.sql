-- One aggregate result set for the Phase 2 business-evidence export.
-- Query after an accepted validation run. No employee or check IDs are exported.
WITH locations_ranked AS (
  SELECT *, row_number() OVER (ORDER BY empty_payment_lists DESC, LocationId) AS ranking
  FROM workspace.applebees_phase2.gold_missing_payment_locations
), coverage AS (
  SELECT '01_coverage' AS section, concept, value, 'Accepted Gold population' AS detail
  FROM workspace.applebees_phase2.gold_coverage
  LATERAL VIEW explode(map(
    'tickets', cast(tickets AS STRING),
    'locations', cast(locations AS STRING),
    'observed_days', cast(observed_days AS STRING),
    'discounted_tickets', cast(discounted_tickets AS STRING),
    'global_discounted_ticket_pct', cast(global_discounted_ticket_pct AS STRING),
    'empty_payment_lists', cast(empty_payment_lists AS STRING)
  )) metrics AS concept, value
), top_locations AS (
  SELECT '02_missing_payments_top3' AS section,
    concat('location_', cast(LocationId AS STRING)) AS concept,
    cast(empty_payment_lists AS STRING) AS value,
    concat(coalesce(location_name, ''), '; share_of_missing_cases_pct=',
      cast(round(pct_of_all_missing_payment_checks, 4) AS STRING),
      '; within_location_missing_pct=', cast(round(empty_payment_pct_within_location, 4) AS STRING)) AS detail
  FROM locations_ranked WHERE ranking <= 3
), top3_total AS (
  SELECT '03_top3_combined_share' AS section, 'share_of_missing_cases_pct' AS concept,
    cast(sum(pct_of_all_missing_payment_checks) AS STRING) AS value,
    'Top 3 locations combined / all checks with empty payment lists' AS detail
  FROM locations_ranked WHERE ranking <= 3
), tips AS (
  SELECT '04_tips' AS section, concept, value, 'Legacy tip magnitude over all accepted checks' AS detail
  FROM workspace.applebees_phase2.gold_tip_statistics
  LATERAL VIEW explode(map(
    'mean_tip_magnitude', cast(mean_tip AS STRING),
    'median_tip_magnitude', cast(median_tip AS STRING),
    'pct_above_mean_magnitude', cast(pct_above_mean_magnitude AS STRING),
    'pct_above_median_magnitude', cast(pct_above_median_magnitude AS STRING)
  )) metrics AS concept, value
), outliers AS (
  SELECT '05_tip_outliers' AS section, 'high_outlier_checks' AS concept,
    cast(count(*) AS STRING) AS value,
    concat('Among checks with available tip data; Q1=', coalesce(cast(max(q1) AS STRING),'NULL'),
      '; Q3=', coalesce(cast(max(q3) AS STRING),'NULL'),
      '; IQR=', coalesce(cast(max(iqr) AS STRING),'NULL'),
      '; threshold=', coalesce(cast(max(upper_threshold) AS STRING),'NULL'),
      '; rule=ABS(sum of payment Gratuity) > Q3 + 1.5 * IQR') AS detail
  FROM workspace.applebees_phase2.gold_tip_outliers
)
SELECT * FROM coverage
UNION ALL SELECT * FROM top_locations
UNION ALL SELECT * FROM top3_total
UNION ALL SELECT * FROM tips
UNION ALL SELECT * FROM outliers
ORDER BY section, concept;
