"""
Lightweight schema and validation utilities for project data.
No external validation libs required.
"""

from __future__ import annotations

from typing import List, Tuple
import pandas as pd


REQUIRED_COLUMNS: List[str] = [
    "ProjectID",
    "ProjectType",
    "Terrain",
    "WeatherImpact",
    "DemandSupply",
    # Baseline planning values (recommended). If missing, we fallback.
    # Keeping them here for documentation; we won't hard-fail if absent.
    # "EstimatedCost",
    # "EstimatedTimeline",
]

OPTIONAL_COLUMNS: List[str] = [
    "TotalCost",
    "Timeline",
    "EstimatedCost",
    "EstimatedTimeline",
    "State",
    "Vendor",
    "MaterialCost",
    "LabourCost",
    "CostEscalation",
    "Resources",
    "ProjectLength",
    "RegulatoryTime",
    "HistoricalDelay",
]


def validate_and_standardize(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate required columns and gently standardize types.

    Returns the (possibly modified) DataFrame and a list of warnings.
    """
    warnings: List[str] = []

    # Check required columns
    missing_required = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    # Soft checks for recommended estimate columns
    if "EstimatedCost" not in df.columns:
        warnings.append("Column 'EstimatedCost' not found; falling back to 'TotalCost' for overrun calc if present.")
    if "EstimatedTimeline" not in df.columns:
        warnings.append("Column 'EstimatedTimeline' not found; falling back to 'Timeline' for overrun calc if present.")

    # Ensure numeric columns are numeric when present
    numeric_candidates = [
        "TotalCost",
        "Timeline",
        "EstimatedCost",
        "EstimatedTimeline",
        "MaterialCost",
        "LabourCost",
        "CostEscalation",
        "Resources",
        "ProjectLength",
        "RegulatoryTime",
        "HistoricalDelay",
    ]
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Basic ID standardization
    if "ProjectID" in df.columns:
        df["ProjectID"] = df["ProjectID"].astype(str)

    return df, warnings


