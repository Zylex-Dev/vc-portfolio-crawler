import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from openai import AsyncOpenAI
from tqdm import tqdm

from pmo_analyzer.assemble import merge_results
from pmo_analyzer.prompt import build_system_prompt, build_user_prompt

MODEL = "deepseek-v4-pro"
CONCURRENCY = 10
MAX_TOKENS = 4096

_SENTINEL: dict = {
    "pmo_score": -1.0,
    "pmo_traj": -1,
    "pmo_mat": -1,
    "pmo_collab": -1,
    "pmo_game": -1,
    "pmo_feedback": -1,
    "pmo_notes": "error",
}


def _parse_text(text: str) -> dict:
    try:
        data = json.loads(text)
        scores = [int(data[k]) for k in ("traj", "mat", "collab", "game", "feedback")]
        return {
            "pmo_score": round(sum(scores) / len(scores), 1),
            "pmo_traj": scores[0],
            "pmo_mat": scores[1],
            "pmo_collab": scores[2],
            "pmo_game": scores[3],
            "pmo_feedback": scores[4],
            "pmo_notes": str(data.get("notes", "")),
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {**_SENTINEL.copy(), "pmo_notes": "parse_error"}


async def score_one(row: dict, client: AsyncOpenAI, system: str) -> dict:
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
        return _parse_text(response.choices[0].message.content)
    except Exception:
        return _SENTINEL.copy()


async def score_all(df: pd.DataFrame) -> dict[str, dict]:
    sem = asyncio.Semaphore(CONCURRENCY)
    results: dict[str, dict] = {}
    system = build_system_prompt()
    client = AsyncOpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
    )

    async def score_row(row: dict) -> None:
        async with sem:
            results[str(row["id"])] = await score_one(row, client, system)

    tasks = [score_row(row.to_dict()) for _, row in df.iterrows()]
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scoring"):
        await coro

    return results


if __name__ == "__main__":
    df = pd.read_csv("data/all_companies.csv")

    print(f"Scoring {len(df)} startups with DeepSeek {MODEL} (concurrency={CONCURRENCY})...")
    results = asyncio.run(score_all(df))

    merged = merge_results(df, results)
    merged.to_csv("data/all_companies_pmo.csv", index=False, encoding="utf-8")

    total = len(merged)
    scored = int((merged["pmo_score"] >= 0).sum())
    errors = int((merged["pmo_score"] == -1).sum())
    print(f"Saved data/all_companies_pmo.csv: {scored}/{total} scored, {errors} errors")
