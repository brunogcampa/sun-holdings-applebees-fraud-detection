# Five-minute English presentation script

Eight main slides, followed by two appendix slides for questions. Rehearse at roughly 130 words per minute. Source citations and execution-status notes are not spoken automatically.

## Slide 1

00:00–00:25. Imagine reviewing more than two million restaurant checks. Which ones deserve attention, and can we trust the numbers behind that decision? Our Phase 2 deliverable builds the data foundation for answering that question. We audited 2,142,846 checks from 127 locations over 115 days. I will explain the workflow, its quality controls and the operational decisions it supports.

## Slide 2

00:25–01:00. The source is a fixed export of complete JSON arrays. Silver standardizes types and checks dates, references and identifiers. It keeps unusable records in quarantine, with reasons, rather than silently deleting them. Gold prepares the business metrics. A separate validation task reconciles those outputs before a run is accepted. We preserve source-file lineage throughout, and keep the historical EDA in a separate schema for comparison.

## Slide 3

01:00–01:40. The transformations protect the meaning of the data. A check is identified by date, location and check ID together. Payments and item discounts become separate child tables. Exploding both arrays in one join could multiply records and inflate totals. A check’s tip is the sum of its payment Gratuity values. We compare the magnitude of that sum because the usual sign is negative. Reference joins add readable location and channel labels without changing the check population.

## Slide 4

01:40–02:20. Quality rules specify an action. Critical reference problems fail publication. Unusable checks go to quarantine, and a nonempty quarantine fails the acceptance gate until review. Empty payment lists remain operational exceptions: they mean no payment record exists in that list, not that a customer necessarily failed to pay. Our independent audit found 3,856 such checks and no duplicate composite keys. Runtime validation also checks that no source rows disappear and that child-event counts and payment sums reconcile.

## Slide 5

02:20–02:55. The job refreshes the pipeline and runs the validator only after a successful update. We allow one concurrent run and one retry for a transient pipeline failure. A failed data check requires investigation. Audit records use run ID plus metric, so retrying the validator does not duplicate audit rows. A second unchanged-source run tests consistency against the prior accepted run. The daily schedule remains paused. Actual run IDs and durations must come from Databricks.

## Slide 6

02:55–03:30. We selected the engineering features for this workload. Batch fits a static historical export. Materialized views store computed results for repeated analysis. Liquid clustering organizes valid checks around date and location filters, but we will measure query profiles before claiming a speed improvement. Expectations give each quality rule a clear warn or fail policy. Streaming remains a future option when a reliable append-only feed exists.

## Slide 7

03:30–04:20. The baseline supports a focused operational question. Locations 87, 1 and 141 account for 71.08 percent of checks whose payment list is empty. That is the share of all missing-payment cases, not the missing-payment rate inside each location. We would prioritize source-system reconciliation there and compare local rates before interpreting concentration. Across all checks, 268,590 have a discount, a weighted rate of 12.53 percent. Gold makes those denominators explicit. These findings come from the audited source and historical EDA. The new pipeline still needs runtime evidence.

## Slide 8

04:20–05:00. Our value is a repeatable foundation for investigation: each metric has a defined population, and each exception has a source and handling policy. The repository, transformations, quality rules and job definition are prepared. Fifteen local checks pass, and the full-source audit reproduces the baseline. The remaining acceptance step is to execute the pipeline and job in Databricks, repeat the run unchanged, and capture the results. Then we can prioritize operational review and develop anomaly models with a clearer understanding of data quality.

## Before the final presentation

The present script accurately states that Databricks deployment and execution are pending. Update those statements only after capturing real successful update/run IDs, validation results and a same-source rerun. Keep the schedule paused until accepted.
