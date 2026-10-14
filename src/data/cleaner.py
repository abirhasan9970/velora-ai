"""
cleaner.py
----------
Data cleaning utilities: drop duplicates, handle missing values,
fix column types, strip whitespace.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CleaningReport:
    """Tracks what changes the cleaner made."""
    rows_before: int = 0
    rows_after: int = 0
    duplicates_removed: int = 0
    missing_filled: dict = field(default_factory=dict)
    columns_dropped: list = field(default_factory=list)
    dtypes_changed: dict = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Rows: {self.rows_before} -> {self.rows_after}",
            f"Duplicates removed: {self.duplicates_removed}",
        ]
        if self.columns_dropped:
            lines.append(f"Columns dropped: {', '.join(self.columns_dropped)}")
        if self.missing_filled:
            filled = ", ".join(f"{k}({v})" for k, v in self.missing_filled.items())
            lines.append(f"Missing values filled: {filled}")
        if self.dtypes_changed:
            changed = ", ".join(f"{k}:{v[0]}->{v[1]}" for k, v in self.dtypes_changed.items())
            lines.append(f"Dtypes changed: {changed}")
        return "\n".join(lines)


def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from object columns."""
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})
    return df


def drop_duplicates(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    report.duplicates_removed = before - len(df)
    return df


def handle_missing(
    df: pd.DataFrame,
    report: CleaningReport,
    numeric_strategy: str = "median",
    categorical_strategy: str = "mode",
    drop_threshold: float = 0.7,
) -> pd.DataFrame:
    """Fill or drop missing values."""
    df = df.copy()
    n = len(df)
    if n == 0:
        return df

    missing_frac = df.isna().mean()
    to_drop = missing_frac[missing_frac > drop_threshold].index.tolist()
    if to_drop:
        df = df.drop(columns=to_drop)
        report.columns_dropped.extend(to_drop)
        logger.info(f"Dropped {len(to_drop)} column(s) with > {drop_threshold:.0%} missing")

    for col in df.columns:
        n_missing = df[col].isna().sum()
        if n_missing == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            if numeric_strategy == "median":
                fill_val = df[col].median()
            elif numeric_strategy == "mean":
                fill_val = df[col].mean()
            else:
                fill_val = 0
            df[col] = df[col].fillna(fill_val)
            report.missing_filled[col] = f"numeric/{numeric_strategy}={fill_val:.3g}"
        else:
            if categorical_strategy == "mode" and not df[col].mode().empty:
                fill_val = df[col].mode().iloc[0]
            else:
                fill_val = "Unknown"
            df[col] = df[col].fillna(fill_val)
            report.missing_filled[col] = f"categorical/{categorical_strategy}='{fill_val}'"

    return df


def try_convert_types(df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
    """Attempt to convert object columns that look numeric or datetime."""
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        original_dtype = str(df[col].dtype)

        try:
            converted = pd.to_numeric(df[col], errors="raise")
            df[col] = converted
            report.dtypes_changed[col] = (original_dtype, str(converted.dtype))
            continue
        except (ValueError, TypeError):
            pass

        try:
            sample = df[col].dropna().head(20)
            if len(sample) >= 5:
                pd.to_datetime(sample, errors="raise")
                df[col] = pd.to_datetime(df[col], errors="coerce")
                report.dtypes_changed[col] = (original_dtype, "datetime64[ns]")
        except Exception:
            pass

    return df


def clean_dataset(
    df: pd.DataFrame,
    *,
    drop_dups: bool = True,
    fill_missing: bool = True,
    convert_types: bool = True,
) -> tuple[pd.DataFrame, CleaningReport]:
    """Run the full cleaning pipeline. Returns (cleaned_df, report)."""
    report = CleaningReport(rows_before=len(df))

    result = df.copy()
    result = strip_whitespace(result)

    if drop_dups:
        result = drop_duplicates(result, report)

    if convert_types:
        result = try_convert_types(result, report)

    if fill_missing:
        result = handle_missing(result, report)

    report.rows_after = len(result)
    logger.info("Cleaning complete:\n" + report.summary())
    return result, report
