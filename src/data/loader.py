"""
loader.py
---------
Loads CSV and Excel files into pandas DataFrames with encoding detection
and clear error messages.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".tsv"}
_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]


class DataLoadError(Exception):
    """Raised when a data file cannot be loaded."""


def _read_csv_with_fallback(path: Path, **kwargs) -> pd.DataFrame:
    """Try multiple encodings for CSV files."""
    last_err: Exception | None = None
    for enc in _ENCODINGS:
        try:
            df = pd.read_csv(path, encoding=enc, **kwargs)
            logger.info(f"Loaded {path.name} with encoding '{enc}'")
            return df
        except UnicodeDecodeError as e:
            last_err = e
            continue
        except pd.errors.ParserError as e:
            try:
                df = pd.read_csv(path, encoding=enc, engine="python", **kwargs)
                logger.info(f"Loaded {path.name} with encoding '{enc}' (python engine)")
                return df
            except Exception as e2:
                last_err = e2
                continue
    raise DataLoadError(
        f"Could not read CSV file '{path.name}'. Tried encodings: {_ENCODINGS}. "
        f"Last error: {last_err}"
    )


def load_dataset(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load a dataset from CSV, TSV, XLSX, or XLS."""
    path = Path(file_path)

    if not path.exists():
        raise DataLoadError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise DataLoadError(
            f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    try:
        if ext == ".csv":
            df = _read_csv_with_fallback(path)
        elif ext == ".tsv":
            df = _read_csv_with_fallback(path, sep="\t")
        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
            logger.info(f"Loaded {path.name} (Excel)")
    except DataLoadError:
        raise
    except Exception as e:
        raise DataLoadError(f"Failed to load {path.name}: {e}") from e

    if df.empty:
        raise DataLoadError(f"File '{path.name}' contains no rows.")

    df.columns = [str(c).strip() for c in df.columns]

    logger.info(f"Dataset shape: {df.shape[0]} rows x {df.shape[1]} columns")
    return df


def get_basic_info(df: pd.DataFrame) -> dict:
    """Return a quick summary of the dataset shape and dtypes."""
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3),
    }
