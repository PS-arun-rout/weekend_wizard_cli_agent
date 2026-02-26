import asyncio
import json
import os
import re
import sys
from typing import Any, Dict, List

from openai import OpenAI
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession
from dotenv import load_dotenv

load_dotenv()


def _client() -> OpenAI:
    api_key = os.getenv("AI_API_TOKEN") or os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("AI_API_TOKEN (or LLM_API_KEY) is not set")
    base_url = os.getenv("LLM_BASE_URL")
    if not base_url:
        raise RuntimeError("LLM_BASE_URL is not set")
    return OpenAI(api_key=api_key, base_url=base_url)


def _model_name() -> str:
    return os.getenv("LLM_MODEL") or "glm 4.7 reasoning"


def _repair_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        snippet = match.group(0)
        try:
            return json.loads(snippet)
        except json.JSONDecodeError:
            pass

    repaired = text.replace("'", '"')
    match = re.search(r"\{.*\}", repaired, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("Could not parse JSON from model output")


def llm_json(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    client = _client()
    resp = client.chat.completions.create(
        model=_model_name(),
        messages=messages,
        temperature=0.2,
    )
    content = resp.choices[0].message.content or ""
    return _repair_json(content.strip())


def llm_text(messages: List[Dict[str, str]]) -> str:
    client = _client()
    resp = client.chat.completions.create(
        model=_model_name(),
        messages=messages,
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()


async def run_agent() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server_fun.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]

            tool_list = ", ".join(tool_names)
            system_prompt = (
                "You are Weekend Wizard. You must respond with ONLY JSON. "
                "Tool call: {\"action\":\"<tool_name>\",\"args\":{...}}. "
                "Finish: {\"action\":\"final\",\"answer\":\"...\"}. "
                "Keep responses friendly, concise, and include real fetched values/links when available. "
                f"Available tools: {tool_list}."
            )

            while True:
                user_input = input("\\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in {"exit", "quit"}:
                    break

                messages: List[Dict[str, str]] = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ]

                tool_calls = 0
                final_answer = ""

                while True:
                    if tool_calls >= 4:
                        final_answer = "I reached the tool-call limit. Please refine your request."
                        break

                    try:
                        model_out = llm_json(messages)
                    except Exception as exc:  # noqa: BLE001
                        messages.append(
                            {
                                "role": "user",
                                "content": f"Observation: JSON parse error: {exc}. Please respond with valid JSON only.",
                            }
                        )
                        tool_calls += 1
                        continue

                    action = model_out.get("action")
                    if action == "final":
                        final_answer = str(model_out.get("answer", "")).strip()
                        break

                    if action not in tool_names:
                        messages.append(
                            {
                                "role": "user",
                                "content": (
                                    f"Observation: Unknown tool '{action}'. "
                                    f"Valid tools: {tool_list}. Please choose a valid action."
                                ),
                            }
                        )
                        tool_calls += 1
                        continue

                    args = model_out.get("args") or {}
                    try:
                        result = await session.call_tool(action, args)
                        observation = result.content
                    except Exception as exc:  # noqa: BLE001
                        observation = {"error": str(exc)}

                    messages.append(
                        {"role": "user", "content": f"Observation: {observation}"}
                    )
                    tool_calls += 1

                if not final_answer:
                    print("\\nAssistant: Sorry, I couldn't complete that.")
                    continue

                reflection_prompt = (
                    "Review the assistant answer for correctness and conciseness. "
                    "If it looks good, reply exactly: looks good. "
                    "Otherwise, provide the corrected answer only."
                )
                reflection_messages = [
                    {"role": "system", "content": reflection_prompt},
                    {"role": "user", "content": final_answer},
                ]
                reflection = llm_text(reflection_messages)

                if re.search(r"looks good", reflection, re.IGNORECASE):
                    print(f"\\nAssistant: {final_answer}")
                else:
                    print(f"\\nAssistant: {reflection}")


if __name__ == "__main__":
    asyncio.run(run_agent())
