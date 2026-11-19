-- Read-only diagnostic: one small result set for sharing after a pipeline update.
-- Expected original snapshot: 2,142,846 raw/assessed/published checks,
-- 115 original files, 0 quarantined/out-of-scope checks and 0 missing dates.
SELECT '01_checks_leidos' AS comprobacion, count(*) AS cantidad
FROM workspace.applebees_phase2.silver_checks_raw
UNION ALL
SELECT '02_checks_evaluados', count(*)
FROM workspace.applebees_phase2.silver_checks_assessed
UNION ALL
SELECT '03_checks_publicados', count(*)
FROM workspace.applebees_phase2.silver_checks
UNION ALL
SELECT '04_checks_cuarentena', count(*)
FROM workspace.applebees_phase2.silver_checks_quarantine
UNION ALL
SELECT '05_checks_fuera_del_periodo', count(*)
FROM workspace.applebees_phase2.silver_checks_out_of_scope
UNION ALL
SELECT '06_archivos_originales', count(DISTINCT source_file)
FROM workspace.applebees_phase2.silver_checks_raw
UNION ALL
SELECT '07_fechas_faltantes', count(*)
FROM workspace.applebees_phase2.gold_missing_dates
UNION ALL
SELECT '08_locations_referencia', count(*)
FROM workspace.applebees_phase2.silver_locations
UNION ALL
SELECT '09_canales_referencia', count(*)
FROM workspace.applebees_phase2.silver_channels
UNION ALL
SELECT concat('10_motivo_', reason), affected_rows
FROM workspace.applebees_phase2.gold_quality_issues
ORDER BY comprobacion;
