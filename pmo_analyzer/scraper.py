import asyncio
import json
from pathlib import Path

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    parts = []

    title = soup.find("title")
    if title:
        parts.append(title.get_text(strip=True))

    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        parts.append(meta["content"])

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    parts.append(soup.get_text(separator=" ", strip=True))
    return " ".join(parts)[:3000]


async def scrape_url(url: str, client: httpx.AsyncClient) -> str:
    try:
        response = await client.get(url, timeout=10, follow_redirects=True)
        return extract_text(response.text)
    except Exception:
        return ""


async def scrape_all(url_map: dict[str, str]) -> dict[str, str]:
    sem = asyncio.Semaphore(50)
    results: dict[str, str] = {}

    async def scrape_one(slug: str, url: str, client: httpx.AsyncClient) -> None:
        async with sem:
            results[slug] = await scrape_url(url, client)

    headers = {"User-Agent": "Mozilla/5.0 (compatible; PMO-Analyzer/1.0)"}
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [scrape_one(slug, url, client) for slug, url in url_map.items() if url]
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Scraping websites"):
            await coro

    return results


if __name__ == "__main__":
    CSV_PATH = Path("data/all_companies.csv")
    OUTPUT_PATH = Path("data/scraped.json")

    df = pd.read_csv(CSV_PATH)

    existing: dict[str, str] = {}
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH) as f:
            existing = json.load(f)

    url_map = {
        str(row["slug"]): str(row["website"])
        for _, row in df.iterrows()
        if str(row.get("slug", "")) not in existing
        and str(row.get("website", "")).startswith("http")
    }

    print(f"Scraping {len(url_map)} URLs (skipping {len(existing)} already done)...")
    new_results = asyncio.run(scrape_all(url_map))

    combined = {**existing, **new_results}
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(combined)} entries to {OUTPUT_PATH}")
