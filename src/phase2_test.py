"""
phase2_test.py
--------------
End-to-end test of the Phase 2 data engine using the sample dataset.
Run: python -m src.phase2_test
"""
from __future__ import annotations

from pathlib import Path

from src.data.analyzer import full_analysis
from src.data.cleaner import clean_dataset
from src.data.loader import get_basic_info, load_dataset
from src.data.visualizer import generate_all_charts
from src.utils.config import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger("phase2_test")


def main() -> int:
    print("\n========== PHASE 2 TEST ==========\n")

    sample = PROJECT_ROOT / "data" / "uploads" / "sample_sales.csv"
    if not sample.exists():
        print(f"[FAIL] Sample file not found: {sample}")
        return 1
    print(f"[OK] Sample file found: {sample}")

    df = load_dataset(sample)
    info = get_basic_info(df)
    print(f"[OK] Loaded: {info['rows']} rows x {info['columns']} columns")
    print(f"     Columns: {info['column_names']}")

    cleaned, report = clean_dataset(df)
    print(f"[OK] Cleaned: {report.rows_before} -> {report.rows_after} rows")
    if report.duplicates_removed:
        print(f"     Duplicates removed: {report.duplicates_removed}")
    if report.dtypes_changed:
        print(f"     Dtypes changed: {list(report.dtypes_changed.keys())}")

    results = full_analysis(cleaned)
    stats = results["summary_stats"]
    print(f"[OK] Analyzed: {stats.shape[0]} numeric columns summarized")
    if results["outliers"]:
        print(f"     Outlier columns: {list(results['outliers'].keys())}")
    else:
        print("     No outliers detected")
    if results["categoricals"]:
        print(f"     Categorical columns: {list(results['categoricals'].keys())}")

    chart_paths = generate_all_charts(cleaned)
    total = sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in chart_paths.values())
    print(f"[OK] Generated {total} chart(s)")
    for kind, paths in chart_paths.items():
        if isinstance(paths, list) and paths:
            for p in paths[:2]:
                print(f"     {kind}: {Path(p).name}")
        elif paths:
            print(f"     {kind}: {Path(paths).name}")

    print("\n========== PHASE 2: SUCCESS ==========\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
