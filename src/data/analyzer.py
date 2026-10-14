"""
analyzer.py
-----------
Statistical analysis: summary stats, correlations, outliers, value counts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return describe() with additional statistics."""
    numeric = df.select_dtypes(include=[np.number])
    if numeric.empty:
        return pd.DataFrame()

    stats = numeric.describe().T
    stats["median"] = numeric.median()
    stats["skew"] = numeric.skew()
    stats["kurtosis"] = numeric.kurtosis()
    stats["missing"] = numeric.isna().sum()
    stats["missing_pct"] = (numeric.isna().mean() * 100).round(2)
    return stats.round(4)


def correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Return correlation matrix for numeric columns."""
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return pd.DataFrame()
    return numeric.corr(method=method).round(4)


def detect_outliers_iqr(df: pd.DataFrame, factor: float = 1.5) -> dict:
    """Detect outliers using the IQR method for each numeric column."""
    result: dict = {}
    numeric = df.select_dtypes(include=[np.number])

    for col in numeric.columns:
        series = numeric[col].dropna()
        if series.empty:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        mask = (numeric[col] < lower) | (numeric[col] > upper)
        count = int(mask.sum())
        if count > 0:
            result[col] = {
                "count": count,
                "pct": round(100 * count / len(numeric), 2),
                "lower": float(lower),
                "upper": float(upper),
                "indices": numeric.index[mask].tolist()[:50],
            }

    return result


def value_counts_summary(df: pd.DataFrame, top_n: int = 10) -> dict:
    """Return top value counts for categorical columns."""
    result: dict = {}
    for col in df.select_dtypes(include=["object", "category"]).columns:
        vc = df[col].value_counts().head(top_n)
        result[col] = {
            "unique": int(df[col].nunique()),
            "top": {str(k): int(v) for k, v in vc.items()},
        }
    return result


def full_analysis(df: pd.DataFrame) -> dict:
    """Run all analyses and return a single dict for reporting."""
    logger.info("Running full analysis")
    return {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "summary_stats": summary_statistics(df),
        "correlations": correlation_matrix(df),
        "outliers": detect_outliers_iqr(df),
        "categoricals": value_counts_summary(df),
    }
