"""
reporter.py
-----------
Generates a Markdown report for a dataset:
- Overview (shape, dtypes, missing values)
- Summary statistics
- Correlations
- Outliers
- Top categorical values
- Generated chart list

Saves the report to reports/<dataset_name>_report.md and returns the path.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from src.data.analyzer import (
    correlation_matrix,
    detect_outliers_iqr,
    summary_statistics,
    value_counts_summary,
)
from src.data.cleaner import CleaningReport, clean_dataset
from src.data.loader import get_basic_info, load_dataset
from src.data.visualizer import generate_all_charts
from src.utils.config import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger(__name__)

REPORTS_DIR = PROJECT_ROOT / "reports"


def _df_to_md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    """Convert a DataFrame to a Markdown table (no extra dependencies)."""
    if df.empty:
        return "_(empty)_"

    df = df.head(max_rows).copy()
    df = df.round(4)

    # Header
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |"]
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")

    # Rows
    for idx, row in df.iterrows():
        cells = [str(idx)] + [f"{v}" if not isinstance(v, float) else f"{v:.4f}" for v in row]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def _series_to_md_table(series: pd.Series) -> str:
    """Convert a Series (index → value) to a Markdown table."""
    lines = ["| value | count |", "|---|---|"]
    for k, v in series.items():
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines)


def generate_report(file_path: str | Path) -> dict:
    """
    Generate a full Markdown report for a dataset.

    Returns:
        {
            "ok": bool,
            "report_path": str | None,
            "charts": dict,
            "error": str | None,
        }
    """
    try:
        path = Path(file_path).resolve()
        df_raw = load_dataset(path)
    except Exception as e:
        return {"ok": False, "report_path": None, "charts": {}, "error": str(e)}

    # Clean
    df, cleaning_report = clean_dataset(df_raw)
    info = get_basic_info(df)

    # Analyze
    stats = summary_statistics(df)
    corr = correlation_matrix(df)
    outliers = detect_outliers_iqr(df)
    cats = value_counts_summary(df)

    # Charts
    charts = generate_all_charts(df)

    # Build the Markdown
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = []
    lines.append(f"# Data Analysis Report — `{path.name}`")
    lines.append("")
    lines.append(f"_Generated: {ts}_")
    lines.append("")

    # 1. Overview
    lines.append("## 1. Overview")
    lines.append("")
    lines.append(f"- **Rows:** {info['rows']}")
    lines.append(f"- **Columns:** {info['columns']}")
    lines.append(f"- **Memory:** {info['memory_mb']} MB")
    lines.append("")
    lines.append("### Columns")
    lines.append("")
    lines.append("| Column | Dtype | Missing | Missing % |")
    lines.append("|---|---|---|---|")
    for col in df.columns:
        missing = int(df[col].isna().sum())
        pct = (missing / len(df) * 100) if len(df) else 0
        lines.append(f"| {col} | {df[col].dtype} | {missing} | {pct:.2f}% |")
    lines.append("")

    # 2. Cleaning summary
    lines.append("## 2. Cleaning Summary")
    lines.append("")
    lines.append(f"- Rows before cleaning: {cleaning_report.rows_before}")
    lines.append(f"- Rows after cleaning: {cleaning_report.rows_after}")
    lines.append(f"- Duplicates removed: {cleaning_report.duplicates_removed}")
    if cleaning_report.columns_dropped:
        lines.append(f"- Columns dropped (too many missing): {', '.join(cleaning_report.columns_dropped)}")
    if cleaning_report.dtypes_changed:
        for col, (old, new) in cleaning_report.dtypes_changed.items():
            lines.append(f"- `{col}`: {old} → {new}")
    lines.append("")

    # 3. Summary statistics
    lines.append("## 3. Summary Statistics (numeric columns)")
    lines.append("")
    if stats.empty:
        lines.append("_No numeric columns._")
    else:
        lines.append(_df_to_md_table(stats))
    lines.append("")

    # 4. Correlations
    lines.append("## 4. Correlations")
    lines.append("")
    if corr.empty:
        lines.append("_Fewer than 2 numeric columns — correlations not computed._")
    else:
        lines.append(_df_to_md_table(corr))
    lines.append("")

    # 5. Outliers
    lines.append("## 5. Outliers (IQR method)")
    lines.append("")
    if not outliers:
        lines.append("_No outliers detected._")
    else:
        lines.append("| Column | Count | % | Lower bound | Upper bound |")
        lines.append("|---|---|---|---|---|")
        for col, o in outliers.items():
            lines.append(
                f"| {col} | {o['count']} | {o['pct']}% | {o['lower']:.4f} | {o['upper']:.4f} |"
            )
    lines.append("")

    # 6. Categorical top values
    lines.append("## 6. Categorical Columns — Top Values")
    lines.append("")
    if not cats:
        lines.append("_No categorical columns._")
    else:
        for col, data in cats.items():
            lines.append(f"### `{col}` ({data['unique']} unique values)")
            lines.append("")
            for val, count in data["top"].items():
                lines.append(f"- `{val}`: {count}")
            lines.append("")

    # 7. Charts
    lines.append("## 7. Generated Charts")
    lines.append("")
    for kind, value in charts.items():
        if isinstance(value, list) and value:
            lines.append(f"### {kind}")
            for p in value:
                lines.append(f"- `{Path(p).name}`")
            lines.append("")
        elif value:
            lines.append(f"### {kind}")
            lines.append(f"- `{Path(value).name}`")
            lines.append("")

    # Write the report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_filename = f"{path.stem}_report.md"
    report_path = REPORTS_DIR / report_filename
    report_path.write_text("\n".join(lines), encoding="utf-8")

    logger.info(f"Report written to {report_path}")
    return {
        "ok": True,
        "report_path": str(report_path),
        "charts": {k: [str(p) for p in v] if isinstance(v, list) else (str(v) if v else None)
                   for k, v in charts.items()},
        "error": None,
    }
