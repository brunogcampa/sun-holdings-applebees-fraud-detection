-- Audit evidence for the first successful complete job run.
-- Change the run_id literal to inspect another run; do not change source data.
SELECT run_id, recorded_at, metric, actual, expected, passed, severity
FROM workspace.applebees_phase2.pipeline_validation_runs
WHERE run_id = '469997930036472'
ORDER BY metric;
