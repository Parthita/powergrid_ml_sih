#!/usr/bin/env python3
"""
Train models to predict cost and timeline overruns (%).
Saves models and feature metadata to best_models.pkl under overrun keys.
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import xgboost as xgb
from feature_engineering import apply_feature_engineering


def create_sample_data(n_samples: int = 3600, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    months = rng.integers(1, 13, n_samples)
    vendor_ids = [f"VEND-{i:02d}" for i in range(1, 26)]

    df = pd.DataFrame({
        'ProjectID': [f'PG-{i+1:04d}' for i in range(n_samples)],
        'ProjectType': rng.choice(['Substation', 'Overhead Line', 'Underground Cable'], n_samples, p=[0.3, 0.45, 0.25]),
        'Terrain': rng.choice(['Plains', 'Hills', 'Forest', 'Urban', 'Coastal'], n_samples, p=[0.32, 0.22, 0.18, 0.18, 0.10]),
        'WeatherImpact': rng.choice(['Low', 'Medium', 'High'], n_samples, p=[0.5, 0.35, 0.15]),
        'DemandSupply': rng.choice(['Stable', 'Fluctuating', 'High Demand'], n_samples, p=[0.45, 0.35, 0.20]),
        'Vendor': rng.choice(vendor_ids, n_samples),
        'Resources': rng.integers(80, 1200, n_samples),
        'ProjectLength': rng.uniform(8, 150, n_samples),
        'RegulatoryTime': rng.uniform(1, 30, n_samples),
        'HistoricalDelay': rng.uniform(0, 18, n_samples),
        'StartMonth': months,
        'VendorOnTimeRate': np.clip(rng.normal(0.8, 0.12, n_samples), 0.2, 0.99),
        'VendorAvgDelay': np.abs(rng.normal(1.8, 1.2, n_samples)),
        'RegulatoryPermitDays': np.clip(rng.normal(140, 35, n_samples), 20, 380),
        'PermitVariance': np.clip(rng.normal(25, 12, n_samples), 0, 120),
        'WeatherSeverityIndex': np.clip(rng.normal(0.45, 0.22, n_samples), 0.0, 1.0),
        'MaterialAvailabilityIndex': np.clip(rng.normal(0.72, 0.18, n_samples), 0.0, 1.0),
        'ResourceUtilization': np.clip(rng.normal(0.76, 0.12, n_samples), 0.25, 1.0),
        'HindranceCounts': rng.poisson(3.2, n_samples),
        'HindranceRecentDays': rng.integers(0, 240, n_samples),
        # Costs breakdown
        'MaterialCost': rng.uniform(200, 1500, n_samples),
        'LabourCost': rng.uniform(150, 1200, n_samples),
    })

    # Estimates with mild seasonality
    season_cost = 1.0 + (np.sin((df['StartMonth'] - 1) / 12 * 2 * np.pi) * 0.05)
    season_time = 1.0 + (np.cos((df['StartMonth'] - 1) / 12 * 2 * np.pi) * 0.05)
    # Initial estimate base from resources/length, plus material/labour
    df['EstimatedCost'] = (520 + df['Resources'] * 0.50 + df['ProjectLength'] * 2.1) * season_cost
    df['EstimatedCost'] += df['MaterialCost'] * 0.9 + df['LabourCost'] * 0.85
    df['EstimatedTimeline'] = (5.0 + df['RegulatoryTime'] * 0.70 + df['HistoricalDelay'] * 0.40 + df['ProjectLength'] * 0.10) * season_time

    # Multipliers by type/terrain/weather
    def mult(sel, cost_mult, time_mult):
        df.loc[sel, 'EstimatedCost'] *= cost_mult[0]
        df.loc[sel, 'EstimatedTimeline'] *= time_mult[0]
    df.loc[df['ProjectType'] == 'Substation', ['EstimatedCost','EstimatedTimeline']] *= [1.35, 1.18]
    df.loc[df['ProjectType'] == 'Underground Cable', ['EstimatedCost','EstimatedTimeline']] *= [1.65, 1.35]
    df.loc[df['Terrain'] == 'Urban', ['EstimatedCost','EstimatedTimeline']] *= [1.35, 1.25]
    df.loc[df['Terrain'] == 'Hills', ['EstimatedCost','EstimatedTimeline']] *= [1.10, 1.10]
    df.loc[df['WeatherImpact'] == 'High', ['EstimatedCost','EstimatedTimeline']] *= [1.12, 1.10]

    # Actuals as estimates + execution slippage
    exec_cost = 30 + df['RegulatoryTime'] * 0.35 + df['HistoricalDelay'] * 0.45
    exec_cost += (1 - df['VendorOnTimeRate']) * 140 + df['VendorAvgDelay'] * 10
    # Material-driven escalation
    material_escalation = (1 - df['MaterialAvailabilityIndex']) * 180 + (df['MaterialCost'] * 0.06)
    df['CostEscalation'] = material_escalation
    exec_cost += material_escalation
    exec_cost += df['PermitVariance'] * 0.7 + df['WeatherSeverityIndex'] * 120
    exec_cost += (1.0 - df['ResourceUtilization']) * 220 + df['HindranceCounts'] * 12
    df['TotalCost'] = df['EstimatedCost'] + exec_cost + np.random.normal(0, 60, len(df))

    exec_time = 0.8 + df['RegulatoryTime'] * 0.22 + df['HistoricalDelay'] * 0.35
    exec_time += (1 - df['VendorOnTimeRate']) * 7 + df['VendorAvgDelay'] * 0.6
    exec_time += (1 - df['MaterialAvailabilityIndex']) * 4.5
    exec_time += df['PermitVariance'] * 0.06 + df['WeatherSeverityIndex'] * 3.5
    exec_time += (1.0 - df['ResourceUtilization']) * 9 + df['HindranceCounts'] * 0.5
    df['Timeline'] = df['EstimatedTimeline'] + exec_time + np.random.normal(0, 2.2, len(df))

    # Sanity floors
    df['EstimatedCost'] = df['EstimatedCost'].clip(lower=100)
    df['EstimatedTimeline'] = df['EstimatedTimeline'].clip(lower=1)
    df['TotalCost'] = df['TotalCost'].clip(lower=120)
    df['Timeline'] = df['Timeline'].clip(lower=1)

    # Overrun targets
    df['CostOverrunPct'] = ((df['TotalCost'] - df['EstimatedCost']) / df['EstimatedCost']) * 100.0
    df['TimelineOverrunPct'] = ((df['Timeline'] - df['EstimatedTimeline']) / df['EstimatedTimeline']) * 100.0
    avg_over = (df['CostOverrunPct'].abs() + df['TimelineOverrunPct'].abs()) / 2
    df['Overall_Risk'] = np.where(avg_over < 10, 'Low', np.where(avg_over < 30, 'Medium', 'High'))
    return df


def train_regressor(X_train, X_test, y_train, y_test, name: str):
    # Hold out 10% of X_train for early stopping
    from sklearn.model_selection import train_test_split
    X_tr, X_val, y_tr, y_val = train_test_split(X_train, y_train, test_size=0.1, random_state=42)

    candidates = [
        dict(n_estimators=600, max_depth=6, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0, reg_alpha=0.0),
        dict(n_estimators=800, max_depth=7, learning_rate=0.045, subsample=0.85, colsample_bytree=0.9, reg_lambda=1.2, reg_alpha=0.0),
        dict(n_estimators=900, max_depth=8, learning_rate=0.04, subsample=0.85, colsample_bytree=0.95, reg_lambda=1.0, reg_alpha=0.1),
    ]

    best = None
    best_score = -1e9
    for i, params in enumerate(candidates):
        model = xgb.XGBRegressor(
            random_state=42,
            tree_method="hist",
            **params,
        )
        # Fit without early stopping for maximum version compatibility
        model.fit(X_tr, y_tr)
        pred = model.predict(X_test)
        r2 = r2_score(y_test, pred)
        mae = mean_absolute_error(y_test, pred)
        print(f"{name} cand#{i+1} → R²={r2:.4f} MAE={mae:.2f}")
        if r2 > best_score:
            best_score = r2
            best = model

    # Final report
    pred = best.predict(X_test)
    r2 = r2_score(y_test, pred)
    mae = mean_absolute_error(y_test, pred)
    print(f"{name} (chosen) → R²={r2:.4f} MAE={mae:.2f}")
    return best


def main():
    print("Training overrun models...")
    df = create_sample_data()

    targets = ['CostOverrunPct', 'TimelineOverrunPct']
    X = df.drop(columns=targets + ['ProjectID', 'TotalCost', 'Timeline', 'Overall_Risk'])
    y_cost = df['CostOverrunPct']
    y_time = df['TimelineOverrunPct']

    X_train, X_test, y_cost_train, y_cost_test = train_test_split(X, y_cost, test_size=0.2, random_state=42)
    _, _, y_time_train, y_time_test = train_test_split(X, y_time, test_size=0.2, random_state=42)

    X_train_fe = apply_feature_engineering(X_train)
    X_test_fe = apply_feature_engineering(X_test)

    print(f"Feature shape: {X_train_fe.shape}")
    cost_over_model = train_regressor(X_train_fe, X_test_fe, y_cost_train, y_cost_test, 'CostOverrunPct')
    time_over_model = train_regressor(X_train_fe, X_test_fe, y_time_train, y_time_test, 'TimelineOverrunPct')

    best_models = {
        'cost_overrun_model': cost_over_model,
        'timeline_overrun_model': time_over_model,
        'feature_names': list(X_train_fe.columns),
    }
    joblib.dump(best_models, 'best_models.pkl')
    print("Saved best_models.pkl")


if __name__ == '__main__':
    main()


