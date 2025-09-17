import csv
from datetime import datetime
import random
import os
import pandas as pd

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUTPUT_DIR, 'farmer_deaths.csv')

random.seed(0)

CAUSES = [
    'Suicide',
    'Poor Crop Growth',
    'Malnutrition',
    'Pesticide Exposure',
    'Debt',
    'Accident',
    'Illness (Non-agri)',
    'Other'
]

REGIONS = ['North', 'South', 'East', 'West', 'Central']

def generate_monthly(year, month):
    rows = []
    for region in REGIONS:
        # base deaths fluctuating with year (simulate worse years)
        base = 20 + (year - 2000) * 0.1 + random.uniform(-5, 5)
        # seasonal effect: sowing/harvest months might see different stress
        seasonal = 5 * (1 if month in (4,5,9,10) else 0.6)
        total = max(1, int(base + seasonal + random.gauss(0, 8)))
        # distribute causes with some correlation to year and region
        cause_weights = [
            0.25 + 0.01*(year-2000),  # suicide slightly increasing
            0.18 - 0.002*(year-2000),
            0.12,
            0.08,
            0.15,
            0.08,
            0.08,
            0.06
        ]
        # small region modifiers
        if region == 'South':
            cause_weights[3] += 0.02  # more pesticide exposure
        if region == 'North':
            cause_weights[1] += 0.02  # poor crop growth

        # normalize
        s = sum(cause_weights)
        cause_weights = [w/s for w in cause_weights]

        counts = [max(0, int(round(w*total + random.gauss(0,1)))) for w in cause_weights]
        # adjust to match total
        diff = total - sum(counts)
        i = 0
        while diff != 0:
            counts[i % len(counts)] += 1 if diff > 0 else -1
            diff = total - sum(counts)
            i += 1

        for cause, cnt in zip(CAUSES, counts):
            rows.append({
                'year': year,
                'month': month,
                'date': f"{year:04d}-{month:02d}-01",
                'region': region,
                'cause': cause,
                'deaths': cnt,
                'farm_size_acres': round(max(0.5, random.gauss(10, 5)),1),
                'avg_income_monthly': int(max(50, random.gauss(200,80)))
            })
    return rows

def main():
    records = []
    for year in range(2000, 2026):
        for month in range(1,13):
            records.extend(generate_monthly(year, month))

    df = pd.DataFrame(records)
    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(df)} rows to {OUT_CSV}")

if __name__ == '__main__':
    main()
