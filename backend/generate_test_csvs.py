#!/usr/bin/env python3
import os
import pandas as pd
from train_overrun import create_sample_data


def make_variant(idx: int) -> pd.DataFrame:
    sizes = [50, 80, 120, 30, 200, 400, 75, 300, 20, 250]
    cost_scales = [0.12, 0.2, 0.5, 0.8, 1.0, 1.2, 2.0, 3.0, 0.06, 4.0]
    n_samples = sizes[(idx - 1) % len(sizes)]
    cost_scale = cost_scales[(idx - 1) % len(cost_scales)]

    base = create_sample_data(n_samples=n_samples, seed=42 + idx)
    # Thin down columns to a practical input set for prediction
    cols = [
        'ProjectID','ProjectType','Terrain','WeatherImpact','DemandSupply','Vendor','State' if 'State' in base.columns else None,
        'Resources','ProjectLength','RegulatoryTime','HistoricalDelay','StartMonth',
        'VendorOnTimeRate','VendorAvgDelay','RegulatoryPermitDays','PermitVariance',
        'WeatherSeverityIndex','MaterialAvailabilityIndex','ResourceUtilization',
        'HindranceCounts','HindranceRecentDays','MaterialCost','LabourCost',
        'EstimatedCost','EstimatedTimeline'
    ]
    cols = [c for c in cols if c is not None and c in base.columns]
    df = base[cols].copy()

    # Variant-specific tweaks
    if idx % 5 == 0:
        # Higher weather severity
        if 'WeatherSeverityIndex' in df.columns:
            df['WeatherSeverityIndex'] = (df['WeatherSeverityIndex'] * 1.25).clip(0, 1)
    if idx % 5 == 1:
        # Vendor delays spike
        if 'VendorAvgDelay' in df.columns:
            df['VendorAvgDelay'] = df['VendorAvgDelay'] * 1.5
        if 'VendorOnTimeRate' in df.columns:
            df['VendorOnTimeRate'] = (df['VendorOnTimeRate'] * 0.9).clip(0, 1)
    if idx % 5 == 2:
        # Material shortage and cost pressure
        if 'MaterialAvailabilityIndex' in df.columns:
            df['MaterialAvailabilityIndex'] = (df['MaterialAvailabilityIndex'] * 0.75).clip(0, 1)
        if 'MaterialCost' in df.columns:
            df['MaterialCost'] = df['MaterialCost'] * 1.2
    if idx % 5 == 3:
        # Regulatory variance up
        if 'PermitVariance' in df.columns:
            df['PermitVariance'] = df['PermitVariance'] * 1.6
        if 'RegulatoryPermitDays' in df.columns:
            df['RegulatoryPermitDays'] = df['RegulatoryPermitDays'] * 1.1
    if idx % 5 == 4:
        # Under-resourced projects
        if 'ResourceUtilization' in df.columns:
            df['ResourceUtilization'] = (df['ResourceUtilization'] * 0.85).clip(0, 1)
        if 'Resources' in df.columns:
            df['Resources'] = (df['Resources'] * 0.9).astype(int)

    # Apply cost scaling to create low-/mid-/high-cost variants
    if 'EstimatedCost' in df.columns:
        df['EstimatedCost'] = df['EstimatedCost'] * cost_scale
    if 'MaterialCost' in df.columns:
        df['MaterialCost'] = df['MaterialCost'] * cost_scale
    if 'LabourCost' in df.columns:
        df['LabourCost'] = df['LabourCost'] * max(0.5, min(cost_scale, 3.0))

    # Ensure expected dtypes
    for c in ['EstimatedCost','EstimatedTimeline','Resources','ProjectLength','RegulatoryTime','HistoricalDelay',
              'VendorOnTimeRate','VendorAvgDelay','RegulatoryPermitDays','PermitVariance','WeatherSeverityIndex',
              'MaterialAvailabilityIndex','ResourceUtilization','HindranceCounts','HindranceRecentDays','MaterialCost','LabourCost']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    df['ProjectID'] = df['ProjectID'].astype(str)
    return df


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'test_csvs')
    os.makedirs(out_dir, exist_ok=True)

    for i in range(1, 11):
        df = make_variant(i)
        out_path = os.path.join(out_dir, f'dummy_variant_{i}.csv')
        df.to_csv(out_path, index=False)
        print(f'Wrote {out_path} ({len(df)} rows)')


if __name__ == '__main__':
    main()


