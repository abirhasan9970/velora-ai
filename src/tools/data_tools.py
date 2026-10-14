"""
data_tools.py
-------------
Concrete tools the agent can call. Each tool:
- takes a simple dict of arguments
- returns a JSON-serializable dict { "ok": bool, "result": ..., "error": str|None }
- never crashes the agent (errors are returned in the result)

Tools wrap our Phase 2 data engine (loader, cleaner, analyzer, visualizer).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.data.analyzer import (
    correlation_matrix,
    detect_outliers_iqr,
    summary_statistics,
    value_counts_summary,
)
from src.data.cleaner import clean_dataset
from src.data.loader import DataLoadError, get_basic_info, load_dataset
from src.data.visualizer import generate_all_charts
from src.utils.config import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Cache loaded DataFrames within a session so we don't re-read files constantly.
_DATASET_CACHE: dict[str, pd.DataFrame] = {}


def _resolve_path(filename: str) -> Path:
    """
    Resolve a filename safely. Only allow files inside data/uploads/.
    Blocks path traversal like '../../etc/passwd'.
    """
    uploads_dir = (PROJECT_ROOT / "data" / "uploads").resolve()
    candidate = (uploads_dir / filename).resolve()

    # Reject if it escapes the uploads dir
    try:
        candidate.relative_to(uploads_dir)
    except ValueError:
        raise ValueError(f"Access denied: '{filename}' is outside the uploads directory.")

    return candidate


def _get_df(filename: str) -> pd.DataFrame:
    """Get a cached, cleaned DataFrame for a file in data/uploads/."""
    if filename not in _DATASET_CACHE:
        path = _resolve_path(filename)
        raw = load_dataset(path)
        cleaned, _ = clean_dataset(raw)
        _DATASET_CACHE[filename] = cleaned
        logger.info(f"Cached dataset '{filename}' ({cleaned.shape})")
    return _DATASET_CACHE[filename]


# ---------------------------------------------------------------- tools

def tool_list_datasets() -> dict[str, Any]:
    """List CSV/Excel files available in data/uploads/."""
    try:
        uploads = PROJECT_ROOT / "data" / "uploads"
        files = sorted(
            [p.name for p in uploads.iterdir() if p.suffix.lower() in {".csv", ".xlsx", ".xls", ".tsv"}]
        )
        return {"ok": True, "result": {"files": files}, "error": None}
    except Exception as e:
        return {"ok": False, "result": None, "error": str(e)}


def tool_describe_dataset(filename: str) -> dict[str, Any]:
    """Return basic info: rows, columns, dtypes, missing values."""
    try:
        df = _get_df(filename)
        info = get_basic_info(df)
        missing = {col: int(df[col].isna().sum()) for col in df.columns}
        info["missing_values"] = missing
        return {"ok": True, "result": info, "error": None}
    except (DataLoadError, ValueError) as e:
        return {"ok": False, "result": None, "error": str(e)}
    except Exception as e:
        logger.exception("tool_describe_dataset failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}


def tool_summary_stats(filename: str) -> dict[str, Any]:
    """Return summary statistics for numeric columns."""
    try:
        df = _get_df(filename)
        stats = summary_statistics(df)
        if stats.empty:
            return {"ok": True, "result": {"message": "No numeric columns found."}, "error": None}
        # Convert to plain dict (JSON-serializable)
        return {"ok": True, "result": stats.to_dict(orient="index"), "error": None}
    except (DataLoadError, ValueError) as e:
        return {"ok": False, "result": None, "error": str(e)}
    except Exception as e:
        logger.exception("tool_summary_stats failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}


def tool_correlations(filename: str) -> dict[str, Any]:
    """Return correlation matrix for numeric columns."""
    try:
        df = _get_df(filename)
        corr = correlation_matrix(df)
        if corr.empty:
            return {"ok": True, "result": {"message": "Fewer than 2 numeric columns."}, "error": None}
        return {"ok": True, "result": corr.to_dict(), "error": None}
    except (DataLoadError, ValueError) as e:
        return {"ok": False, "result": None, "error": str(e)}
    except Exception as e:
        logger.exception("tool_correlations failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}


def tool_outliers(filename: str) -> dict[str, Any]:
    """Detect outliers using the IQR method."""
    try:
        df = _get_df(filename)
        result = detect_outliers_iqr(df)
        return {"ok": True, "result": result, "error": None}
    except (DataLoadError, ValueError) as e:
        return {"ok": False, "result": None, "error": str(e)}
    except Exception as e:
        logger.exception("tool_outliers failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}


def tool_value_counts(filename: str, top_n: int = 10) -> dict[str, Any]:
    """Return top value counts for categorical columns."""
    try:
        df = _get_df(filename)
        result = value_counts_summary(df, top_n=int(top_n))
        return {"ok": True, "result": result, "error": None}
    except (DataLoadError, ValueError) as e:
        return {"ok": False, "result": None, "error": str(e)}
    except Exception as e:
        logger.exception("tool_value_counts failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}


def tool_generate_charts(filename: str) -> dict[str, Any]:
    """Generate all charts for a dataset and return file paths."""
    try:
        df = _get_df(filename)
        charts = generate_all_charts(df)
        # Convert Path objects to strings
        out = {}
        for kind, value in charts.items():
            if isinstance(value, list):
                out[kind] = [str(p) for p in value]
            elif value is not None:
                out[kind] = str(value)
            else:
                out[kind] = None
        return {"ok": True, "result": out, "error": None}
    except (DataLoadError, ValueError) as e:
        return {"ok": False, "result": None, "error": str(e)}
    except Exception as e:
        logger.exception("tool_generate_charts failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}


def clear_cache() -> None:
    """Clear the DataFrame cache (useful in tests)."""
    _DATASET_CACHE.clear()
    