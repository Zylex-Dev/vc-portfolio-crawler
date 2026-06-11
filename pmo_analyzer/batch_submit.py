import json
from pathlib import Path

import anthropic
import pandas as pd
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from pmo_analyzer.prompt import build_system_prompt, build_user_prompt


def build_requests(df: pd.DataFrame, scraped: dict[str, str]) -> list[Request]:
    system = build_system_prompt()
    requests = []
    for _, row in df.iterrows():
        scraped_text = scraped.get(str(row["slug"]), "")
        requests.append(
            Request(
                custom_id=str(row["id"]),
                params=MessageCreateParamsNonStreaming(
                    model="claude-haiku-4-5",
                    max_tokens=256,
                    system=system,
                    messages=[{"role": "user", "content": build_user_prompt(row.to_dict(), scraped_text)}],
                ),
            )
        )
    return requests


if __name__ == "__main__":
    client = anthropic.Anthropic()

    df = pd.read_csv("data/all_companies.csv")
    scraped: dict[str, str] = {}
    scraped_path = Path("data/scraped.json")
    if scraped_path.exists():
        with open(scraped_path) as f:
            scraped = json.load(f)

    requests = build_requests(df, scraped)
    print(f"Submitting batch of {len(requests)} requests...")

    batch = client.messages.batches.create(requests=requests)

    Path("data/batch_id.txt").write_text(batch.id)
    print(f"Batch submitted: {batch.id}")
    print(f"Monitor: https://console.anthropic.com/batches/{batch.id}")
