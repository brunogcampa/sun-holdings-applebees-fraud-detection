# Data contract and analytical definitions

## Scope and identifiers

The original export covers 2026-04-28 through 2026-08-20 inclusive. Source files
are complete multiline JSON arrays, not JSON Lines or a change-data feed. Raw
files are immutable inputs for this snapshot; their hashes are recorded by the
independent source audit. Expected inventory: 115 files and 115 observed dates.

Check key: `business_date + LocationId + check_id`. Check ID alone is not unique.
Negative IDs are preserved. Null keys are rejected from the analytical population.
All rows sharing a duplicate key are quarantined because no trustworthy update
timestamp establishes which copy should survive. No probabilistic matching is used.

An event identifier consists of the check key plus level, item position (if any)
and discount position. Payment identity adds payment position. These source
positions are stable within a fixed file and avoid merging repeated legitimate events.

## Nulls, typing and quarantine

| Condition | Detection | Handling |
|---|---|---|
| Malformed JSON/type coercion | Explicit Spark schema and `_corrupt_record` | Retain raw evidence and quarantine; gate fails |
| Invalid business date | `try_cast(BusinessDate AS DATE)` returns NULL | Quarantine |
| Missing key/reference | Missing check/location or no matching location/channel ID | Quarantine |
| Duplicate check key | Window count over the composite key > 1 | Quarantine every copy |
| Missing item/discount list | Source array is NULL | Quarantine rather than assert no items/discounts |
| Null numeric field inside payment/discount event | Explicit null counters after type parsing | Quarantine; no reliable zero is fabricated |
| Empty Payments | Non-null array of length 0 | Keep as an operational exception with `tip_available=false` |
| Null Payments | Array is NULL | Keep a separate missing-data flag; `tip_available=false` |
| Invalid/absent timestamp | `try_cast` is NULL | Monitor, retain the check, exclude from future duration analysis |
| Close before open | Parsed closing timestamp < opening timestamp | Monitor, do not add 24 hours without a source-system rule |
| Valid record outside requested dates | `in_scope=false` | Separate out-of-scope output; not a quality failure |
| Null/duplicate dimension ID | Fail expectation | Stop publication to prevent a join multiplying rows |

Warn expectations record failures while keeping evidence. Fail expectations stop
updates. The post-run gate additionally rejects any nonempty quarantine. These
are complementary policies, not a claim that the pipeline atomically commits all
tables together. Operators must withhold acceptance when the gate fails.

## Amounts and denominators

- `gratuity_raw = SUM(Payments[].Gratuity)` per check. Its magnitude is
  `ABS(gratuity_raw)`, not the sum of absolute per-payment tips. Mixed signs can offset.
- The legacy all-check distribution coalesces missing/empty payment lists to zero.
  Availability counts explicitly show which zeros lack an observed payment record.
  Comparisons with/without discounts use `tip_available=true`.
- Greater tip means greater magnitude: ABS(-4) > ABS(-3). Strictly greater than
  the mean/median excludes ties. Global legacy mean includes all published checks.
- Discounted check means at least one ticket or item discount event, even if its
  amount is zero. Count distinct checks independently from discount events.
- Global rate = discounted checks / all published checks. Daily mean averages
  daily rates equally. Location mean averages location rates equally. They answer
  different questions and are never substituted for one another.
- Category share = events of the category / events of the same discount level.
  Location share within category = category events at that location / all events
  of that category and level. Top-five ranking breaks ties by LocationId.
- Employee/manager shares retain all events, including missing/sentinel IDs, in
  the denominator before filtering identifiable actors for ranking.
- Missing-payment case share and within-location missing-payment rate have
  different denominators. Both appear in the output.
- `Amount` and `Gratuity` retain source signs. Currency and tax/sales reconciliation
  require a business definition. No row labels a raw payment sum as net revenue.
- Ticket-level and item-level discount amounts stay separate because overlap is
  not confirmed. Event-level mean magnitude averages `ABS(Amount)` at one level.
- Names retain original spelling for auditability. A trimmed uppercase companion
  supports investigation. It does not merge category IDs or validate their meanings.

## Outlier rule

Within checks with available tip data, Q1 is the 25th percentile and Q3 the 75th
percentile of tip magnitude. IQR = Q3 - Q1. A high outlier exceeds
Q3 + 1.5 × IQR. For example, if Q1=0 and Q3=6, the threshold is 15 source amount
units. This example explains the rule; it is not the measured threshold of this dataset.
Gold stores the actual quartiles and threshold alongside every flagged check.
The rule is descriptive, sensitive to population mix and not proof of fraud.

## Trust boundaries

Data quality checks support consistency, validity, completeness and uniqueness.
They do not establish accounting accuracy without reconciliation to the POS or
ledger. Roles of EmployeeId/ManagerId and definitions/permissions for TASTE,
GST CORECT, SERVERERR, KITCHNERR, WALKOUT and TEMP remain unconfirmed internally.
Differences in tips are associations, not evidence that discounts cause them.
Activity concentration needs exposure measures and operational context before
being interpreted as an individual risk score.

## Reconciliation and repeatability

The validator requires raw assessed rows = published + quarantined + valid
out-of-scope rows, Gold check totals = Silver totals, and child payment/discount
counts = sums of their parent array lengths. Signed payment and tip sums reconcile
with a 0.01 absolute tolerance for floating point aggregation differences.

Two runs with the same selected source fields must produce the same published
check fingerprint. The fingerprint test covers published checks, not bitwise
identity of every Gold dataset. Gold aggregates reconcile separately. The local
SHA256 manifest covers complete input file bytes; the runtime fingerprint covers
the explicitly selected source schema. Neither is presented as a cryptographic
proof of the entire pipeline's runtime correctness.
