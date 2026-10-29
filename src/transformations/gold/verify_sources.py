"""Independent full-source audit. Does not execute or validate the Spark runtime.
Writes only aggregate evidence; private check/employee identifiers are not exported.
"""
import json
from pathlib import Path
from collections import Counter
from datetime import date, datetime
import hashlib
import time

import sys
base = Path(sys.argv[1]).resolve() if len(sys.argv)>1 and not sys.argv[1].startswith(chr(45)) else Path(__file__).resolve().parents[3]
out = base / 'phase2/evidence'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def valid_date(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def assess(check, location_ids, channel_ids):
    reasons = []
    if valid_date(check.get('BusinessDate')) is None:
        reasons.append('INVALID_DATE')
    for field, reason in [('Id', 'MISSING_CHECK_ID'), ('LocationId', 'MISSING_LOCATION_ID')]:
        if check.get(field) is None:
            reasons.append(reason)
    if check.get('LocationId') not in location_ids:
        reasons.append('UNKNOWN_LOCATION')
    if check.get('RevenueCenterId') not in channel_ids:
        reasons.append('UNKNOWN_CHANNEL')
    for field, reason in [('ItemsSold', 'MISSING_ITEM_LIST'), ('Discounts', 'MISSING_DISCOUNT_LIST')]:
        if check.get(field) is None:
            reasons.append(reason)
    payments = check.get('Payments') or []
    discounts = list(check.get('Discounts') or [])
    for item in check.get('ItemsSold') or []:
        if item:
            discounts.extend(item.get('Discounts') or [])
    if any(p is None or p.get('Amount') is None or p.get('Gratuity') is None for p in payments):
        reasons.append('INVALID_PAYMENT_NUMERIC')
    if any(d is None or d.get('Amount') is None for d in discounts):
        reasons.append('INVALID_DISCOUNT_NUMERIC')
    return reasons


def main():
    out.mkdir(parents=True, exist_ok=True)
    began = time.monotonic()
    locations = read(base/'dimensions/locations/locations.json')
    channels = read(base/'dimensions/revenue_centers/revenueCenters.json')
    location_ids = {r['Id'] for r in locations}
    channel_ids = {r['Id'] for r in channels}
    counters, issues, daily, per_location = Counter(), Counter(), {}, {}
    seen, duplicate_keys, days, observed_locations = set(), set(), set(), set()
    manifest = []
    files = sorted((base/'facts/checks').rglob('*.json'))
    for number, path in enumerate(files, 1):
        contents = path.read_bytes()
        manifest.append({'relative_path':path.relative_to(base).as_posix(), 'sha256':hashlib.sha256(contents).hexdigest(), 'bytes':len(contents)})
        records = json.loads(contents.decode('utf-8-sig'))
        for c in records:
            counters['raw_checks'] += 1
            dt = valid_date(c.get('BusinessDate'))
            reasons = assess(c, location_ids, channel_ids)
            issues.update(reasons)
            if reasons:
                counters['rows_with_quality_issues'] += 1
            if dt is not None:
                days.add(str(dt))
                if not (date(2026,4,28) <= dt <= date(2026,8,20)):
                    counters['out_of_scope'] += 1
                    continue
            observed_locations.add(c.get('LocationId'))
            key = (c.get('BusinessDate'),c.get('LocationId'),c.get('Id'))
            if key in seen:
                counters['duplicate_excess_rows'] += 1
                duplicate_keys.add(key)
            else:
                seen.add(key)
            p = c.get('Payments') or []
            tip = sum((r or {}).get('Gratuity') or 0 for r in p)
            discounts = c.get('Discounts') or []
            item_events = [d for i in c.get('ItemsSold') or [] for d in (i or {}).get('Discounts') or []]
            discounted = bool(discounts or item_events)
            counters['discounted_checks'] += discounted
            counters['ticket_discount_events'] += len(discounts)
            counters['item_discount_events'] += len(item_events)
            counters['payment_events'] += len(p)
            counters['empty_payment_lists'] += c.get('Payments') == []
            counters['null_payment_lists'] += c.get('Payments') is None
            counters['tip_negative' if tip<0 else 'tip_positive' if tip>0 else 'tip_zero'] += 1
            for group, value in [(daily,str(dt)),(per_location,c.get('LocationId'))]:
                group.setdefault(value,Counter()).update({'tickets':1,'discounted':int(discounted)})
        if number % 10 == 0 or number == len(files):
            print(f'{number}/{len(files)} files, {counters["raw_checks"]:,} checks',flush=True)
    counters['duplicate_keys'] = len(duplicate_keys)
    results = {'evidence_type':'independent_python_source_audit','spark_pipeline_executed':False,
               'files':len(files),'locations':len(observed_locations),'observed_days':len(days),
               'start_date':min(days),'end_date':max(days),'counts':dict(counters),'quality_issues':dict(issues),
               'dimension_ids_unique':len(location_ids)==len(locations) and len(channel_ids)==len(channels),
               'daily_discounted_pct_mean':sum(100*x['discounted']/x['tickets'] for x in daily.values())/len(daily),
               'location_discounted_pct_mean':sum(100*x['discounted']/x['tickets'] for x in per_location.values())/len(per_location),
               'elapsed_seconds':round(time.monotonic()-began,2)}
    (out/'source_audit.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    (out/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2),flush=True)


if __name__ == '__main__':
    main()
