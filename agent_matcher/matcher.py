import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from openai import AsyncOpenAI
from tqdm import tqdm

from agent_matcher.agents_loader import load_agents
from agent_matcher.assemble import build_agent_pivot_df, build_assignment_df
from agent_matcher.prompt import build_system_prompt, build_user_prompt

MODEL = "deepseek-v4-pro"
CONCURRENCY = 10
MAX_TOKENS = 4096

_SENTINEL: dict = {"agent_id": -1, "relevance": -1, "rationale": "error"}


def _parse_response(text: str) -> dict:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        data = json.loads(text[start:end])
        return {
            "agent_id": int(data["agent_id"]),
            "relevance": int(data["relevance"]),
            "rationale": str(data.get("rationale", "")),
        }
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return {**_SENTINEL.copy(), "rationale": "parse_error"}


async def match_one(row: dict, client: AsyncOpenAI, system: str) -> dict:
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": build_user_prompt(row)},
            ],
            extra_body={"thinking": {"type": "enabled"}},
        )
        return _parse_response(response.choices[0].message.content)
    except Exception:
        return _SENTINEL.copy()


async def match_all(df: pd.DataFrame, agents: list[dict]) -> dict[str, dict]:
    sem = asyncio.Semaphore(CONCURRENCY)
    results: dict[str, dict] = {}
    system = build_system_prompt(agents)
    client = AsyncOpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
    )

    async def match_row(row: dict) -> None:
        async with sem:
            results[str(row["id"])] = await match_one(row, client, system)

    tasks = [match_row(row.to_dict()) for _, row in df.iterrows()]
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Matching"):
        await coro

    return results


if __name__ == "__main__":
    df = pd.read_csv("data/edu_companies_pmo.csv")
    agents = load_agents()

    print(
        f"Matching {len(df)} startups against {len(agents)} agents "
        f"with {MODEL} (concurrency={CONCURRENCY})..."
    )
    results = asyncio.run(match_all(df, agents))

    assignment = build_assignment_df(df, results, agents)
    assignment.to_csv("data/startup_agent_assignment.csv", index=False, encoding="utf-8")

    pivot = build_agent_pivot_df(assignment, agents)
    pivot.to_csv("data/agent_startups.csv", index=False, encoding="utf-8")

    matched = int((~assignment["assigned_agent"].isin(["unmatched", "error"])).sum())
    unmatched = int((assignment["assigned_agent"] == "unmatched").sum())
    errors = int((assignment["assigned_agent"] == "error").sum())
    print(f"Saved. matched={matched}, unmatched={unmatched}, errors={errors}")
