"""
upload_tools.py
---------------
Agent-callable tools for uploading files and generating full reports.
Wraps src.data.uploader and src.data.reporter.
"""
from __future__ import annotations

from typing import Any

from src.data.reporter import generate_report
from src.data.uploader import upload_file
from src.utils.logger import get_logger

logger = get_logger(__name__)


def tool_upload_dataset(source_path: str) -> dict[str, Any]:
    """
    Copy a file from anywhere on disk into data/uploads/, safely.
    """
    try:
        result = upload_file(source_path)
        return {"ok": result["ok"], "result": result if result["ok"] else None,
                "error": result.get("error")}
    except Exception as e:
        logger.exception("tool_upload_dataset failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}


def tool_generate_report(filename: str) -> dict[str, Any]:
    """
    Generate a full Markdown report for a dataset in data/uploads/.
    """
    from src.tools.data_tools import _resolve_path, _get_df  # reuse safe resolver
    try:
        path = _resolve_path(filename)  # validates it's inside uploads/
        # Touch the cache to make sure the file loads
        _ = _get_df(filename)

        report = generate_report(path)
        return {"ok": report["ok"],
                "result": {"report_path": report["report_path"],
                           "charts": report["charts"]} if report["ok"] else None,
                "error": report.get("error")}
    except Exception as e:
        logger.exception("tool_generate_report failed")
        return {"ok": False, "result": None, "error": f"Unexpected error: {e}"}
    