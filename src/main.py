"""
main.py
-------
Phase 1 sanity check: verifies the environment, config, and logging all work.
Run from project root:  python -m src.main
"""
from __future__ import annotations

import platform
import sys
from pathlib import Path

from src.utils.config import PROJECT_ROOT, get_settings
from src.utils.logger import get_logger


def _check(label: str, ok: bool, detail: str = "") -> bool:
    marker = "[OK]" if ok else "[FAIL]"
    line = f"{marker}  {label}"
    if detail:
        line += f"  ->  {detail}"
    print(line)
    return ok


def main() -> int:
    logger = get_logger("main")
    logger.info("Starting AI Agent - Phase 1 environment check")

    print("\n========= AI Agent - Phase 1 Environment Check =========\n")

    ok = True

    ok &= _check(
        "Python version",
        sys.version_info >= (3, 10),
        f"{platform.python_version()} (need >= 3.10)",
    )

    ok &= _check("Operating system", True, f"{platform.system()} {platform.release()}")

    ok &= _check("Project root found", PROJECT_ROOT.exists(), str(PROJECT_ROOT))

    required_dirs = [
        "src", "src/agent", "src/data", "src/llm", "src/tools", "src/ui", "src/utils",
        "tests", "data", "data/uploads", "data/outputs", "reports", "logs", "docs", ".streamlit",
    ]
    missing = [d for d in required_dirs if not (PROJECT_ROOT / d).is_dir()]
    ok &= _check("Folder structure", not missing, "all present" if not missing else f"missing: {missing}")

    env_file = PROJECT_ROOT / ".env"
    ok &= _check(".env file present", env_file.is_file(), str(env_file))

    try:
        settings = get_settings()
        _check("Settings load", True, f"env={settings.app_env}, log={settings.log_level}, provider={settings.llm_provider}")
        _check("OpenAI key configured", bool(settings.openai_api_key and not settings.openai_api_key.startswith("sk-your")),
               "yes" if settings.openai_api_key and not settings.openai_api_key.startswith("sk-your") else "placeholder (fill in Phase 3)")
    except Exception as e:
        ok = False
        _check("Settings load", False, str(e))

    logger.info("Logging pipeline test message")
    log_file = PROJECT_ROOT / "logs" / "app.log"
    ok &= _check("Log file written", log_file.is_file(), str(log_file))

    print("\n========================================================")
    if ok:
        print("PHASE 1 RESULT: SUCCESS - environment is ready.")
        print("Next: confirm to your instructor, then proceed to Phase 2.")
    else:
        print("PHASE 1 RESULT: ISSUES DETECTED - fix the [FAIL] items above.")
    print("========================================================\n")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
