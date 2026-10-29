# Verified Gold findings

Scope: April 28 through August 20, 2026, inclusive. Evidence exported after
accepted job run `904398544867578` on October 29, 2026.

## Coverage and reliability

Gold contains 2,142,846 published checks from 127 locations over 115 days. All
115 original files retain traceable paths. Raw, assessed and published row counts
reconcile. Both complete jobs pass all 28 audit results, including parent-child
event counts and signed payment/tip sums within the declared aggregation tolerance.
Duplicates, corrupt records, quarantine and missing dates each have zero rows.

The reference dimension contains 185 locations, while 127 locations appear in the
check population. Business rates use the observed population, not every reference ID.

## Missing-payment records and review priorities

There are 3,856 checks with empty payment lists, approximately 0.1800% of all
published checks. These are missing payment records in this export. They require
source-system reconciliation before drawing a conclusion about an unpaid bill.

| Location | Checks with empty Payments | Share of all empty-payment cases | Empty-payment rate within the location |
|---|---:|---:|---:|
| 87, Warsaw | 1,335 | 34.6214% | 4.5649% |
| 1, Topeka | 928 | 24.0664% | 3.4199% |
| 141, Prescott | 478 | 12.3963% | 3.6092% |

These three locations account for **2,741 of 3,856 cases, or 71.0840%**. Start
source-system reconciliation there to cover most cases with a focused location
review. Compare the within-location rate and transaction volume when prioritizing
further investigation. The displayed case shares and local rates have different
denominators. Rounded percentages can have a small summation difference.

## Discount coverage

268,590 checks have at least one discount event, **12.534265% of all checks**.
This is the weighted rate across the whole period. A mean of daily percentages
answers a different question. Keep ticket-level and item-level amounts separate
until their accounting overlap and business definitions are confirmed.

## Tip magnitudes and outliers

The legacy all-check analysis sums `Payments[].Gratuity` for each check and then
takes the absolute value for comparisons. It coalesces unavailable payment data
to zero, so the following statistics include retained checks without a payment record.

| Measure | Verified result |
|---|---:|
| Mean tip magnitude, all published checks | 4.122923 source amount units |
| Median tip magnitude, all published checks | 0 |
| Checks strictly above the mean magnitude | 38.739601% |
| Checks strictly above the median magnitude | 48.032616% |

For the IQR rule, the population includes only checks with available payment/tip
data. Q1 is 0 and Q3 is 7. IQR = Q3 - Q1 = 7. The measured upper threshold is
Q3 + 1.5 * IQR = **17.5 source amount units**. There are **77,856 checks** with
tip magnitude strictly above that threshold. Values equal to 17.5 are excluded.

An outlier is a descriptive review signal. Assess payment channel, check value and
operational context before interpreting a large tip as an anomaly requiring action.
Currency and actor roles still need business confirmation. Negative source signs
are preserved in the underlying tables.

## Business actions

1. Reconcile empty-payment checks at locations 87, 1 and 141 against the POS lifecycle.
2. Confirm discount-code definitions and authorization rules with operations.
3. Compare exceptions within similar channels and transaction-size groups before assigning risk.

The pipeline supports reproducible investigation. It does not establish fraud,
ledger accuracy, causal effects of discounts on tips or a model's predictive performance.

## Traceability

- Query: [final_gold_evidence.sql](final_gold_evidence.sql)
- Gold export: [runtime_gold_evidence.csv](runtime_gold_evidence.csv)
- First job audit: [runtime_job_1_validation.csv](runtime_job_1_validation.csv)
- Second job audit: [runtime_job_2_validation.csv](runtime_job_2_validation.csv)
- Scope and handling rules: [DATA_CONTRACT.md](DATA_CONTRACT.md)
- Runtime IDs, fingerprints and observed durations: [runtime_evidence.json](runtime_evidence.json)
