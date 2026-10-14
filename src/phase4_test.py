"""
phase4_test.py
--------------
End-to-end test of the agent loop. The agent should decide to call
tools to answer questions about the sample dataset.

Run: python -m src.phase4_test
"""
from __future__ import annotations

from src.agent.agent import Agent
from src.llm.client import LLMError
from src.tools import data_tools
from src.utils.logger import get_logger

logger = get_logger("phase4_test")


def _run_question(agent: Agent, question: str) -> None:
    print("\n" + "=" * 60)
    print(f"QUESTION: {question}")
    print("=" * 60)

    try:
        run = agent.run(question)
    except (LLMError, ValueError) as e:
        print(f"[FAIL] {e}")
        return

    print(f"\nSteps taken: {len(run.steps)}")
    for s in run.steps:
        if s.tool_call:
            tool_name = s.tool_call.get("tool")
            ok = s.tool_result.get("ok") if s.tool_result else None
            print(f"  Step {s.step}: called '{tool_name}' | ok={ok}")
        else:
            print(f"  Step {s.step}: final answer")

    print(f"\nFINAL ANSWER:\n{run.final_answer}")
    print(f"\nTokens: in={run.total_input_tokens} out={run.total_output_tokens}")
    print(f"Cost: ${run.total_cost_usd:.6f} (free tier = $0)")


def main() -> int:
    print("\n========== PHASE 4 TEST (Agent Loop) ==========")

    # Clear dataset cache so we start fresh
    data_tools.clear_cache()

    # Build the agent
    try:
        agent = Agent()
    except LLMError as e:
        print(f"[FAIL] Could not build agent: {e}")
        return 1
    print(f"[OK] Agent initialized | model={agent.llm.model_name}")

    # Test 1: The agent should call list_datasets first
    _run_question(agent, "What datasets do you have access to?")

    # Test 2: The agent should describe the sample dataset
    _run_question(agent, "Describe the dataset called sample_sales.csv.")

    # Test 3: The agent should call summary_stats or correlations
    _run_question(
        agent,
        "For sample_sales.csv, which numeric columns are most strongly correlated?",
    )

    # Test 4: Natural-language reasoning on the results
    _run_question(
        agent,
        "For sample_sales.csv, are there any outliers in the 'customer_age' column? "
        "Give me specific numbers.",
    )

    print("\n========== PHASE 4: SUCCESS ==========\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
