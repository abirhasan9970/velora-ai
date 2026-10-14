"""
phase3_test.py
--------------
Verifies the Gemini LLM client works end-to-end.
Run: python -m src.phase3_test
"""
from __future__ import annotations

from src.llm.client import LLMClient, LLMError, count_tokens
from src.llm.prompts import SYSTEM_PROMPT_GENERAL
from src.utils.logger import get_logger

logger = get_logger("phase3_test")


def main() -> int:
    print("\n========== PHASE 3 TEST (Gemini) ==========\n")

    # 1) Token counting sanity
    sample = "Hello, this is a test of token counting."
    n = count_tokens(sample)
    print(f"[OK] Token count for sample: {n}")

    # 2) Client init
    try:
        client = LLMClient()
    except LLMError as e:
        print(f"[FAIL] Could not initialize client: {e}")
        return 1
    print(f"[OK] Client initialized | model={client.model_name}")

    # 3) Simple chat
    prompt = "In one sentence, explain what a pandas DataFrame is."
    print(f"[..] Sending prompt: {prompt!r}")

    try:
        response = client.chat(prompt, system_prompt=SYSTEM_PROMPT_GENERAL, max_tokens=128)
    except LLMError as e:
        print(f"[FAIL] Chat failed: {e}")
        return 1

    print(f"[OK] Response received")
    print(f"     Text: {response.text.strip()}")
    print(f"     Input tokens:  {response.input_tokens}")
    print(f"     Output tokens: {response.output_tokens}")
    print(f"     Est. cost USD: ${response.estimated_cost_usd:.6f}  (free tier = $0)")
    print(f"     Finish reason: {response.finish_reason}")

    # 4) Multi-turn: pass history
    history = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response.text},
    ]
    followup = "Now give me one real-world example use case."
    print(f"\n[..] Follow-up: {followup!r}")
    try:
        r2 = client.chat(followup, system_prompt=SYSTEM_PROMPT_GENERAL,
                         history=history, max_tokens=128)
    except LLMError as e:
        print(f"[FAIL] Follow-up failed: {e}")
        return 1

    print(f"[OK] Follow-up response received")
    print(f"     Text: {r2.text.strip()}")
    print(f"     Est. cost USD: ${r2.estimated_cost_usd:.6f}")

    total_cost = response.estimated_cost_usd + r2.estimated_cost_usd
    print(f"\n[OK] Total estimated cost this test: ${total_cost:.6f}")
    print(f"     (Free tier usage = actually $0.00)")

    print("\n========== PHASE 3: SUCCESS ==========\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
