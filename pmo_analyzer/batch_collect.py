import json
import time
from pathlib import Path

import anthropic
import pandas as pd

_SENTINEL: dict = {
    "pmo_score": -1.0,
    "pmo_traj": -1,
    "pmo_mat": -1,
    "pmo_collab": -1,
    "pmo_game": -1,
    "pmo_feedback": -1,
    "pmo_notes": "error",
}


def parse_result(result) -> dict:
    if result.result.type != "succeeded":
        return _SENTINEL.copy()

    text = next((b.text for b in result.result.message.content if b.type == "text"), "")
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


def merge_results(df: pd.DataFrame, results: dict[str, dict]) -> pd.DataFrame:
    rows = [{"id": int(k), **v} for k, v in results.items()]
    score_df = pd.DataFrame(rows)
    return df.merge(score_df, on="id", how="left")


if __name__ == "__main__":
    client = anthropic.Anthropic()
    batch_id = Path("data/batch_id.txt").read_text().strip()

    print(f"Polling batch {batch_id}...")
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            break
        counts = batch.request_counts
        print(f"  {batch.processing_status} — processing: {counts.processing}, waiting 60s...")
        time.sleep(60)

    counts = batch.request_counts
    print(f"Batch done — succeeded: {counts.succeeded}, errored: {counts.errored}")

    parsed: dict[str, dict] = {}
    for result in client.messages.batches.results(batch_id):
        parsed[result.custom_id] = parse_result(result)

    df = pd.read_csv("data/all_companies.csv")
    merged = merge_results(df, parsed)
    merged.to_csv("data/all_companies_pmo.csv", index=False, encoding="utf-8")

    total = len(merged)
    scored = int((merged["pmo_score"] >= 0).sum())
    errors = int((merged["pmo_score"] == -1).sum())
    print(f"Saved data/all_companies_pmo.csv: {scored}/{total} scored, {errors} errors")
