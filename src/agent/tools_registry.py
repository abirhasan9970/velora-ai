"""
tools_registry.py
-----------------
Central registry mapping tool names to (function, description, schema).
The agent uses this to know what tools exist and how to call them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.tools import data_tools
from src.tools import upload_tools


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict
    function: Callable


_REGISTRY = {}


def register(spec: ToolSpec) -> None:
    _REGISTRY[spec.name] = spec


def get_tool(name: str):
    return _REGISTRY.get(name)


def all_tools() -> list:
    return list(_REGISTRY.values())


def tool_catalog_text() -> str:
    lines = []
    for spec in _REGISTRY.values():
        params = ", ".join(f"{k}: {v}" for k, v in spec.parameters.items()) or "no parameters"
        lines.append(f"- {spec.name}({params})  ->  {spec.description}")
    return "\n".join(lines)


# ---------------------------------------------------------- register tools

register(ToolSpec(
    name="list_datasets",
    description="List all CSV/Excel files available in the uploads directory.",
    parameters={},
    function=data_tools.tool_list_datasets,
))

register(ToolSpec(
    name="describe_dataset",
    description="Return shape, column names, data types, and missing-value counts for a dataset.",
    parameters={"filename": "Name of the file, e.g. 'sample_sales.csv'"},
    function=data_tools.tool_describe_dataset,
))

register(ToolSpec(
    name="summary_stats",
    description="Return summary statistics (mean, std, quartiles, skew, kurtosis) for numeric columns.",
    parameters={"filename": "Name of the file"},
    function=data_tools.tool_summary_stats,
))

register(ToolSpec(
    name="correlations",
    description="Return the Pearson correlation matrix between numeric columns.",
    parameters={"filename": "Name of the file"},
    function=data_tools.tool_correlations,
))

register(ToolSpec(
    name="outliers",
    description="Detect outliers using the IQR method for each numeric column.",
    parameters={"filename": "Name of the file"},
    function=data_tools.tool_outliers,
))

register(ToolSpec(
    name="value_counts",
    description="Return the top-N most frequent values for each categorical column.",
    parameters={
        "filename": "Name of the file",
        "top_n": "How many top values to return (default 10)",
    },
    function=data_tools.tool_value_counts,
))

register(ToolSpec(
    name="generate_charts",
    description="Generate histograms, correlation heatmap, boxplots, and bar charts for a dataset.",
    parameters={"filename": "Name of the file"},
    function=data_tools.tool_generate_charts,
))

register(ToolSpec(
    name="upload_dataset",
    description=(
        "Copy a CSV/Excel file from anywhere on disk into the project uploads folder. "
        "Provide the full file path."
    ),
    parameters={"source_path": "Absolute path to the file on disk"},
    function=upload_tools.tool_upload_dataset,
))

register(ToolSpec(
    name="generate_report",
    description=(
        "Generate a full Markdown analysis report for a dataset in uploads/. "
        "Returns the report file path and chart paths."
    ),
    parameters={"filename": "Name of the file in the uploads folder"},
    function=upload_tools.tool_generate_report,
))
