"""
visualizer.py
-------------
Generate charts from a DataFrame and save them as PNG files.
Uses matplotlib with the non-interactive 'Agg' backend.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.utils.config import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports" / "charts"


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def plot_histograms(df: pd.DataFrame, output_dir: Path | None = None, max_cols: int = 6) -> list[Path]:
    """Save a histogram for each numeric column (up to max_cols)."""
    out = _ensure_dir(output_dir or DEFAULT_OUTPUT_DIR)
    numeric = df.select_dtypes(include=[np.number])
    paths: list[Path] = []

    for i, col in enumerate(numeric.columns[:max_cols]):
        fig, ax = plt.subplots(figsize=(7, 4))
        numeric[col].dropna().hist(ax=ax, bins=30, color="#2563EB", edgecolor="white")
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        p = out / f"hist_{i+1:02d}_{_safe(col)}.png"
        fig.savefig(p, dpi=100)
        plt.close(fig)
        paths.append(p)

    logger.info(f"Saved {len(paths)} histogram(s)")
    return paths


def plot_correlation_heatmap(df: pd.DataFrame, output_dir: Path | None = None) -> Path | None:
    """Save a correlation heatmap if there are at least 2 numeric columns."""
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return None

    out = _ensure_dir(output_dir or DEFAULT_OUTPUT_DIR)
    corr = numeric.corr()

    fig, ax = plt.subplots(figsize=(max(6, len(corr) * 0.6), max(5, len(corr) * 0.6)))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    ax.set_title("Correlation Heatmap")

    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center",
                    color="white" if abs(corr.values[i, j]) > 0.5 else "black", fontsize=8)

    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    p = out / "correlation_heatmap.png"
    fig.savefig(p, dpi=100)
    plt.close(fig)
    logger.info("Saved correlation heatmap")
    return p


def plot_boxplots(df: pd.DataFrame, output_dir: Path | None = None, max_cols: int = 6) -> list[Path]:
    """Save boxplots for numeric columns."""
    out = _ensure_dir(output_dir or DEFAULT_OUTPUT_DIR)
    numeric = df.select_dtypes(include=[np.number])
    paths: list[Path] = []

    for i, col in enumerate(numeric.columns[:max_cols]):
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.boxplot(numeric[col].dropna(), vert=False, patch_artist=True,
                   boxprops=dict(facecolor="#93C5FD"))
        ax.set_title(f"Boxplot of {col}")
        ax.set_xlabel(col)
        fig.tight_layout()
        p = out / f"box_{i+1:02d}_{_safe(col)}.png"
        fig.savefig(p, dpi=100)
        plt.close(fig)
        paths.append(p)

    logger.info(f"Saved {len(paths)} boxplot(s)")
    return paths


def plot_categorical_bars(df: pd.DataFrame, output_dir: Path | None = None,
                          max_cols: int = 4, top_n: int = 10) -> list[Path]:
    """Save bar charts for the top categories in each categorical column."""
    out = _ensure_dir(output_dir or DEFAULT_OUTPUT_DIR)
    cats = df.select_dtypes(include=["object", "category"])
    paths: list[Path] = []

    for i, col in enumerate(cats.columns[:max_cols]):
        counts = df[col].value_counts().head(top_n)
        if counts.empty:
            continue
        fig, ax = plt.subplots(figsize=(8, 4))
        counts.plot(kind="bar", ax=ax, color="#2563EB", edgecolor="white")
        ax.set_title(f"Top {top_n} values of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout()
        p = out / f"bar_{i+1:02d}_{_safe(col)}.png"
        fig.savefig(p, dpi=100)
        plt.close(fig)
        paths.append(p)

    logger.info(f"Saved {len(paths)} bar chart(s)")
    return paths


def generate_all_charts(df: pd.DataFrame, output_dir: Path | None = None) -> dict:
    """Run every chart generator and return a dict of created file paths."""
    out = _ensure_dir(output_dir or DEFAULT_OUTPUT_DIR)
    logger.info(f"Generating charts into {out}")
    return {
        "histograms": plot_histograms(df, out),
        "heatmap": plot_correlation_heatmap(df, out),
        "boxplots": plot_boxplots(df, out),
        "bar_charts": plot_categorical_bars(df, out),
    }


def _safe(name: str) -> str:
    """Make a filename-safe version of a column name."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in str(name))[:40]
