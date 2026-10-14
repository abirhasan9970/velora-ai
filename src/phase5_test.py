"""
phase5_test.py
--------------
End-to-end test of Phase 5: upload + auto report.
Run: python -m src.phase5_test
"""
from __future__ import annotations

from pathlib import Path

from src.data.reporter import generate_report
from src.data.uploader import upload_file
from src.tools import data_tools, upload_tools
from src.utils.config import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger("phase5_test")


def main() -> int:
    print("\n========== PHASE 5 TEST ==========\n")

    # Clear the dataset cache
    data_tools.clear_cache()

    # ---- 1. Upload the messy file (already in uploads, but simulate external upload)
    source = PROJECT_ROOT / "data" / "uploads" / "messy_customers.csv"
    if not source.exists():
        print(f"[FAIL] Sample file missing: {source}")
        return 1
    print(f"[OK] Source file: {source}")

    result = upload_file(source)
    if not result["ok"]:
        print(f"[FAIL] Upload failed: {result['error']}")
        return 1
    print(f"[OK] Uploaded -> {result['filename']} ({result['size_bytes']} bytes)")
    if result["renamed"]:
        print(f"     (renamed to avoid collision)")

    uploaded_name = result["filename"]

    # ---- 2. Test the upload tool wrapper
    print("\n--- Testing upload_tools.tool_upload_dataset ---")
    tool_result = upload_tools.tool_upload_dataset(str(source))
    print(f"  ok={tool_result['ok']}  filename="
          f"{tool_result['result']['filename'] if tool_result['ok'] else None}")

    # ---- 3. Generate the report on the messy file
    print(f"\n--- Generating report for {uploaded_name} ---")
    report = generate_report(PROJECT_ROOT / "data" / "uploads" / uploaded_name)
    if not report["ok"]:
        print(f"[FAIL] Report generation failed: {report['error']}")
        return 1

    print(f"[OK] Report saved to: {report['report_path']}")

    chart_count = sum(
        len(v) if isinstance(v, list) else (1 if v else 0)
        for v in report["charts"].values()
    )
    print(f"[OK] Charts generated: {chart_count}")

    # ---- 4. Test the agent-callable report tool
    print(f"\n--- Testing upload_tools.tool_generate_report ---")
    tr = upload_tools.tool_generate_report(uploaded_name)
    print(f"  ok={tr['ok']}")
    if tr["ok"]:
        print(f"  report_path={tr['result']['report_path']}")

    # ---- 5. Show the report preview
    print("\n--- Report Preview (first 40 lines) ---")
    report_path = Path(report["report_path"])
    content = report_path.read_text(encoding="utf-8").splitlines()
    for line in content[:40]:
        print(line)

    print("\n========== PHASE 5: SUCCESS ==========\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
