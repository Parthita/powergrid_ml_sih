#!/usr/bin/env python3
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
from feature_engineering import apply_feature_engineering
from schema import validate_and_standardize


app = FastAPI(title="PowerGrid ML API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models = None
feature_names = None


def load_models():
    global models, feature_names
    if models is None:
        models = joblib.load('best_models.pkl')
        feature_names = models.get('feature_names')


def predict_df(df: pd.DataFrame) -> pd.DataFrame:
    load_models()
    df, _ = validate_and_standardize(df)

    X = apply_feature_engineering(df.drop(columns=[c for c in ["TotalCost", "Timeline"] if c in df.columns]))
    X = X.select_dtypes(include=[np.number])
    if feature_names is not None:
        X = X.reindex(columns=feature_names, fill_value=0)

    # Overrun models take precedence
    if "cost_overrun_model" in models and "timeline_overrun_model" in models:
        cost_over = models["cost_overrun_model"].predict(X)
        time_over = models["timeline_overrun_model"].predict(X)
        cost_base = df["EstimatedCost"] if "EstimatedCost" in df.columns else df.get("TotalCost", pd.Series(0, index=df.index))
        time_base = df["EstimatedTimeline"] if "EstimatedTimeline" in df.columns else df.get("Timeline", pd.Series(0, index=df.index))
        df["Predicted_Cost"] = cost_base * (1.0 + cost_over / 100.0)
        df["Predicted_Timeline"] = time_base * (1.0 + time_over / 100.0)
        df["Cost_Overrun_Pct"] = cost_over
        df["Timeline_Overrun_Pct"] = time_over
    else:
        df["Predicted_Cost"] = models["cost_model"].predict(X)
        df["Predicted_Timeline"] = models["timeline_model"].predict(X)

    # Overall risk
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


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV upload")

    try:
        out_df = predict_df(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Return JSON rows
    return {
        "rows": out_df.to_dict(orient="records")
    }


