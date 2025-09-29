#!/usr/bin/env python3
"""
CLI to generate predictions and overrun metrics for the React dashboard.
Input CSV -> augmented CSV with Predicted_* columns.
"""

import argparse
import sys
import pandas as pd
import numpy as np
import joblib

from feature_engineering import apply_feature_engineering
from schema import validate_and_standardize


def compute_overruns(df: pd.DataFrame) -> pd.DataFrame:
    cost_baseline = None
    timeline_baseline = None
    if "EstimatedCost" in df.columns:
        cost_baseline = df["EstimatedCost"]
    elif "TotalCost" in df.columns:
        cost_baseline = df["TotalCost"]

    if "EstimatedTimeline" in df.columns:
        timeline_baseline = df["EstimatedTimeline"]
    elif "Timeline" in df.columns:
        timeline_baseline = df["Timeline"]

    if cost_baseline is not None and "Predicted_Cost" in df.columns:
        with np.errstate(divide="ignore", invalid="ignore"):
            df["Cost_Overrun_Pct"] = ((df["Predicted_Cost"] - cost_baseline) / cost_baseline) * 100.0

    if timeline_baseline is not None and "Predicted_Timeline" in df.columns:
        with np.errstate(divide="ignore", invalid="ignore"):
            df["Timeline_Overrun_Pct"] = ((df["Predicted_Timeline"] - timeline_baseline) / timeline_baseline) * 100.0

    def risk_row(row) -> str:
        cost_over = abs(row.get("Cost_Overrun_Pct", np.nan))
        time_over = abs(row.get("Timeline_Overrun_Pct", np.nan))
        vals = [v for v in [cost_over, time_over] if np.isfinite(v)]
        if not vals:
            return "Unknown"
        avg = float(np.mean(vals))
        if avg < 10:
            return "Low"
        if avg < 30:
            return "Medium"
        return "High"

    df["Overall_Risk"] = df.apply(risk_row, axis=1)
    return df


def main(argv=None):
    parser = argparse.ArgumentParser(description="Predict costs and timelines, compute overruns")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--models", default="best_models.pkl", help="Path to trained models pickle")
    args = parser.parse_args(argv)

    models = joblib.load(args.models)

    df = pd.read_csv(args.input)
    df, warnings = validate_and_standardize(df)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f" - {w}")

    X = apply_feature_engineering(df.drop(columns=[c for c in ["TotalCost", "Timeline"] if c in df.columns]))
    X = X.select_dtypes(include=[np.number])
    feature_names = models.get("feature_names")
    if feature_names is not None:
        X = X.reindex(columns=feature_names, fill_value=0)

    # Predict handling both legacy absolute models and new overrun models
    if "cost_overrun_model" in models and "timeline_overrun_model" in models:
        cost_over = models["cost_overrun_model"].predict(X)
        time_over = models["timeline_overrun_model"].predict(X)
        # Baselines for reconstruction
        cost_base = df["EstimatedCost"] if "EstimatedCost" in df.columns else df.get("TotalCost", pd.Series(0, index=df.index))
        time_base = df["EstimatedTimeline"] if "EstimatedTimeline" in df.columns else df.get("Timeline", pd.Series(0, index=df.index))
        df["Predicted_Cost"] = cost_base * (1.0 + cost_over / 100.0)
        df["Predicted_Timeline"] = time_base * (1.0 + time_over / 100.0)
        df["Cost_Overrun_Pct"] = cost_over
        df["Timeline_Overrun_Pct"] = time_over
    else:
        df["Predicted_Cost"] = models["cost_model"].predict(X)
        df["Predicted_Timeline"] = models["timeline_model"].predict(X)

    if "Cost_Overrun_Pct" not in df.columns or "Timeline_Overrun_Pct" not in df.columns:
        df = compute_overruns(df)

    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()


