"""
AI Agent - General Purpose Assistant
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from src.agent.tools_registry import get_tool, tool_catalog_text
from src.llm.client import LLMClient, LLMError
from src.utils.logger import get_logger

logger = get_logger(__name__)

MAX_STEPS = 6


SYSTEM_PROMPT_AGENT = """You are Velora AI, a friendly, intelligent, and helpful general-purpose AI assistant.

ABOUT YOU:
- You can answer ANY question on ANY topic: general knowledge, science, history, coding, math, writing, advice, casual conversation, jokes, current events, and more.
- You are multilingual — you understand and respond in English, Bangla, and other languages.
- You are warm, conversational, and helpful.
- You never refuse a reasonable request.

CORE BEHAVIOR:
1. Answer questions directly and concisely (2-5 sentences for simple questions, more for complex ones).
2. If the user speaks Bangla, respond in Bangla. If English, respond in English.
3. For coding questions, provide clean, well-commented code.
4. For math, show your reasoning step by step.
5. For opinions or advice, be thoughtful and balanced.
6. For creative writing, be imaginative.
7. If you do not know something, say so honestly — never make up facts.

CONVERSATION STYLE:
- Be friendly but professional.
- Use emojis sparingly (only when appropriate).
- Keep answers focused — do not ramble.
- If the question is ambiguous, ask ONE clarifying question.

TOOL USE:
You have access to the following tools (use only if the user request clearly needs them):

{tool_catalog}

If you need to use a tool, respond ONLY with this exact JSON format:
{{"tool": "<tool_name>", "arguments": {{...}}}}

Otherwise, respond with plain natural language.

RULES:
- Never invent tool names.
- Never claim to have capabilities you do not have.
- Never output the JSON format unless you are actually calling a tool.
- Always prioritize helping the user.
"""


@dataclass
class AgentStep:
    step: int
    thought: str = ""
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    tool_result: str = ""
    final_answer: str = ""


@dataclass
class AgentRun:
    question: str
    final_answer: str = ""
    steps: list = field(default_factory=list)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    _called_tools: set = field(default_factory=set)


def _extract_tool_call(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
    try:
        data = json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except Exception:
            return None
    if not isinstance(data, dict):
        return None
    if "tool" not in data:
        return None
    return data


class Agent:
    """General-purpose conversational agent backed by an LLM."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()
        self.system_prompt = SYSTEM_PROMPT_AGENT.format(tool_catalog=tool_catalog_text())

    def run(self, question: str, max_steps: int = MAX_STEPS, image_bytes: bytes | None = None, image_mime: str = "image/jpeg") -> AgentRun:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        logger.info(f"Agent run start | question={question!r}")
        run = AgentRun(question=question, final_answer="")
        run._called_tools = set()

        history: list[dict] = []

        for step_num in range(1, max_steps + 1):
            try:
                response = self.llm.chat(
                    question,
                    system_prompt=self.system_prompt,
                    history=history,
                    temperature=0.7,
                    max_tokens=2048,
                    image_bytes=image_bytes,
                    image_mime=image_mime,
                )
            except LLMError as e:
                run.final_answer = f"Sorry, I ran into an error talking to my brain: {e}"
                logger.error(run.final_answer)
                return run

            run.total_input_tokens += response.input_tokens
            run.total_output_tokens += response.output_tokens
            run.total_cost_usd += response.estimated_cost_usd

            llm_text = response.text.strip()

            tool_call = _extract_tool_call(llm_text)
            if tool_call is None:
                run.final_answer = llm_text
                run.steps.append(AgentStep(step=step_num, final_answer=llm_text))
                logger.info("Agent produced final answer")
                return run

            tool_name = tool_call.get("tool", "")
            arguments = tool_call.get("arguments", {}) or {}
            if not isinstance(arguments, dict):
                arguments = {}

            spec = get_tool(tool_name)
            if spec is None:
                history.append({"role": "assistant", "content": llm_text})
                history.append({
                    "role": "user",
                    "content": f"TOOL RESULT: Unknown tool '{tool_name}'. Please use only listed tools or answer directly.",
                })
                continue

            try:
                result = spec.func(**arguments)
                result_str = json.dumps(result, default=str)[:3000]
            except Exception as e:
                result_str = f"Tool error: {e}"

            run._called_tools.add(tool_name)
            run.steps.append(AgentStep(
                step=step_num,
                tool_name=tool_name,
                tool_args=arguments,
                tool_result=result_str,
            ))

            history.append({"role": "assistant", "content": llm_text})
            history.append({"role": "user", "content": f"TOOL RESULT: {result_str}"})

        run.final_answer = "I went through many steps but could not finish. Please rephrase the question."
        return run
