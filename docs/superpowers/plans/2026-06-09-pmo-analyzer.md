# PMO Analyzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 3-step pipeline that scrapes startup websites, scores all 3535 startups against the PMO educational framework via Anthropic Batches API, and outputs `data/all_companies_pmo.csv`.

**Architecture:** Three standalone scripts (`scraper.py`, `batch_submit.py`, `batch_collect.py`) under `pmo_analyzer/`. `prompt.py` holds the scoring rubric and prompt builder shared by the other scripts. Run sequentially: scrape → submit batch → collect results. Scraping uses async httpx (50 concurrent). LLM scoring uses `claude-haiku-4-5` via Batches API (50% cost discount vs real-time).

**Tech Stack:** Python 3.11+, httpx, BeautifulSoup4, anthropic SDK, pandas, tqdm, pytest, pytest-asyncio

---

### Task 1: Project setup

**Files:**
- Modify: `requirements.txt`
- Create: `pmo_analyzer/__init__.py`
- Create: `tests/pmo_analyzer/__init__.py`
- Create: `pytest.ini`

- [ ] **Step 1: Update requirements.txt**

Replace the contents of `requirements.txt` with:

```
requests>=2.31
beautifulsoup4>=4.12
lxml>=5.0
pytest>=8.0
httpx>=0.27
tqdm>=4.0
anthropic>=0.40
pandas>=2.2
pytest-asyncio>=0.23
```

- [ ] **Step 2: Create package skeleton**

```bash
mkdir -p pmo_analyzer tests/pmo_analyzer
touch pmo_analyzer/__init__.py tests/pmo_analyzer/__init__.py
```

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
asyncio_mode = auto
```

- [ ] **Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages install cleanly, no errors.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt pmo_analyzer/__init__.py tests/pmo_analyzer/__init__.py pytest.ini
git commit -m "feat: scaffold pmo_analyzer package and add dependencies"
```

---

### Task 2: PMO prompt module

**Files:**
- Create: `pmo_analyzer/prompt.py`
- Create: `tests/pmo_analyzer/test_prompt.py`

- [ ] **Step 1: Write failing tests**

Create `tests/pmo_analyzer/test_prompt.py`:

```python
from pmo_analyzer.prompt import build_system_prompt, build_user_prompt


def test_system_prompt_contains_all_five_instruments():
    prompt = build_system_prompt()
    for instrument in ["TRAJ", "MAT", "COLLAB", "GAME", "FEEDBACK"]:
        assert instrument in prompt, f"Missing instrument: {instrument}"


def test_system_prompt_requests_json_output():
    assert "JSON" in build_system_prompt()


def test_user_prompt_includes_name_sectors_stage_description():
    row = {
        "name": "LearnAI",
        "sectors": "AI;EdTech",
        "stage": "Seed",
        "description": "Adaptive tutoring for kids.",
    }
    result = build_user_prompt(row, "Homepage: AI-powered learning")
    assert "LearnAI" in result
    assert "AI;EdTech" in result
    assert "Seed" in result
    assert "Adaptive tutoring for kids." in result
    assert "AI-powered learning" in result


def test_user_prompt_shows_na_when_scraped_text_is_empty():
    row = {"name": "Co", "sectors": "EdTech", "stage": "Series A", "description": "desc"}
    assert "N/A" in build_user_prompt(row, "")


def test_user_prompt_shows_na_when_scraped_text_is_none():
    row = {"name": "Co", "sectors": "EdTech", "stage": "Series A", "description": "desc"}
    assert "N/A" in build_user_prompt(row, None)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/pmo_analyzer/test_prompt.py -v
```

Expected: `ModuleNotFoundError: No module named 'pmo_analyzer.prompt'`

- [ ] **Step 3: Create pmo_analyzer/prompt.py**

```python
def build_system_prompt() -> str:
    return """You are an EdTech expert evaluating startups against the PMO \
(Персонализированная Модель Образования) framework.

Score each of the 5 PMO instruments from 0 to 10:

TRAJ — Персонализированная Траектория: Does the student create and own their learning path?
  9-10: learning path creation/ownership is the core product feature
  7-8:  clear path customization for individual goals
  5-6:  some sequencing choices available to the learner
  3-4:  minor personalization options exist
  0-2:  fixed curriculum, no path personalization

MAT — Учебные Материалы: Does content adapt to individual interests, pace, or learning style?
  9-10: AI-driven or deep adaptive content personalization
  7-8:  explicit multi-format/multi-level content adaptation
  5-6:  some content variety or learner filtering
  3-4:  limited format options
  0-2:  static, one-size-fits-all content

COLLAB — Совместная Деятельность: Are there rich peer or mentor interaction features?
  9-10: collaborative projects, co-creation, community are core to the product
  7-8:  significant social learning features
  5-6:  discussion boards or some peer interaction
  3-4:  basic comments or forums only
  0-2:  solo learning only, no social features

GAME — Геймификация и Визуализация: Are game mechanics and visual progress central?
  9-10: gamification is the primary engagement mechanism
  7-8:  meaningful badges, levels, challenges, visual dashboards
  5-6:  some gamification elements present
  3-4:  basic progress indicators only
  0-2:  no game mechanics or visual engagement

FEEDBACK — Обратная Связь: Is feedback personalized, immediate, and actionable?
  9-10: AI-driven real-time personalized feedback
  7-8:  automated detailed feedback tied to individual progress
  5-6:  structured feedback with some personalization
  3-4:  generic automated feedback
  0-2:  no feedback or only manual/delayed feedback

Respond ONLY with valid JSON and no markdown fences:
{"traj": <int 0-10>, "mat": <int 0-10>, "collab": <int 0-10>, "game": <int 0-10>, \
"feedback": <int 0-10>, "notes": "<one sentence in Russian summarizing the main finding>"}"""


def build_user_prompt(row: dict, scraped_text: str | None) -> str:
    website_content = scraped_text if scraped_text else "N/A"
    return (
        f"Name: {row.get('name', 'N/A')}\n"
        f"Sectors: {row.get('sectors', 'N/A')}\n"
        f"Stage: {row.get('stage', 'N/A')}\n"
        f"Description: {row.get('description', 'N/A')}\n"
        f"Website content: {website_content}"
    )
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/pmo_analyzer/test_prompt.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add pmo_analyzer/prompt.py tests/pmo_analyzer/test_prompt.py
git commit -m "feat: add PMO prompt builder with tests"
```

---

### Task 3: Async website scraper

**Files:**
- Create: `pmo_analyzer/scraper.py`
- Create: `tests/pmo_analyzer/test_scraper.py`

- [ ] **Step 1: Write failing tests**

Create `tests/pmo_analyzer/test_scraper.py`:

```python
import httpx
from unittest.mock import AsyncMock, MagicMock

from pmo_analyzer.scraper import extract_text, scrape_url


def test_extract_text_includes_page_title():
    html = "<html><head><title>My School App</title></head><body><p>Learn here</p></body></html>"
    assert "My School App" in extract_text(html)


def test_extract_text_includes_meta_description():
    html = '<html><head><meta name="description" content="Best tutoring platform"></head><body></body></html>'
    assert "Best tutoring platform" in extract_text(html)


def test_extract_text_removes_script_content():
    html = "<html><body><script>alert('xss')</script><p>Real content</p></body></html>"
    result = extract_text(html)
    assert "alert" not in result
    assert "Real content" in result


def test_extract_text_removes_style_content():
    html = "<html><body><style>.red { color: red }</style><p>Visible text</p></body></html>"
    result = extract_text(html)
    assert ".red" not in result
    assert "Visible text" in result


def test_extract_text_truncates_to_3000_characters():
    html = f"<html><body><p>{'a' * 5000}</p></body></html>"
    assert len(extract_text(html)) <= 3000


async def test_scrape_url_returns_extracted_text_on_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "<html><head><title>EduTech</title></head><body><p>We teach</p></body></html>"
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await scrape_url("https://example.com", mock_client)
    assert "EduTech" in result
    assert "We teach" in result


async def test_scrape_url_returns_empty_string_on_timeout():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

    result = await scrape_url("https://example.com", mock_client)
    assert result == ""


async def test_scrape_url_returns_empty_string_on_any_error():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=Exception("connection refused"))

    result = await scrape_url("https://example.com", mock_client)
    assert result == ""
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/pmo_analyzer/test_scraper.py -v
```

Expected: `ModuleNotFoundError: No module named 'pmo_analyzer.scraper'`

- [ ] **Step 3: Create pmo_analyzer/scraper.py**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/pmo_analyzer/test_scraper.py -v
```

Expected: `8 passed`

- [ ] **Step 5: Commit**

```bash
git add pmo_analyzer/scraper.py tests/pmo_analyzer/test_scraper.py
git commit -m "feat: add async website scraper with tests"
```

---

### Task 4: Batch request builder

**Files:**
- Create: `pmo_analyzer/batch_submit.py`
- Create: `tests/pmo_analyzer/test_batch_submit.py`

- [ ] **Step 1: Write failing tests**

Create `tests/pmo_analyzer/test_batch_submit.py`:

```python
import pandas as pd

from pmo_analyzer.batch_submit import build_requests


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"id": 1, "slug": "company-a", "name": "Alpha", "sectors": "EdTech", "stage": "Seed",     "description": "Adaptive learning"},
        {"id": 2, "slug": "company-b", "name": "Beta",  "sectors": "AI",     "stage": "Series A", "description": "AI tutor"},
    ])


def test_build_requests_returns_one_request_per_row():
    assert len(build_requests(_sample_df(), {})) == 2


def test_build_requests_custom_id_equals_startup_id_as_string():
    requests = build_requests(_sample_df(), {})
    ids = {r["custom_id"] for r in requests}
    assert ids == {"1", "2"}


def test_build_requests_uses_scraped_text_when_slug_present():
    scraped = {"company-a": "great platform for students"}
    requests = build_requests(_sample_df(), scraped)
    request_a = next(r for r in requests if r["custom_id"] == "1")
    content = request_a["params"]["messages"][0]["content"]
    assert "great platform for students" in content


def test_build_requests_uses_na_when_slug_missing_from_scraped():
    requests = build_requests(_sample_df(), {})
    content = requests[0]["params"]["messages"][0]["content"]
    assert "N/A" in content


def test_build_requests_uses_haiku_model():
    requests = build_requests(_sample_df(), {})
    assert requests[0]["params"]["model"] == "claude-haiku-4-5"


def test_build_requests_max_tokens_is_256():
    requests = build_requests(_sample_df(), {})
    assert requests[0]["params"]["max_tokens"] == 256
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/pmo_analyzer/test_batch_submit.py -v
```

Expected: `ModuleNotFoundError: No module named 'pmo_analyzer.batch_submit'`

- [ ] **Step 3: Create pmo_analyzer/batch_submit.py**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/pmo_analyzer/test_batch_submit.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add pmo_analyzer/batch_submit.py tests/pmo_analyzer/test_batch_submit.py
git commit -m "feat: add batch request builder with tests"
```

---

### Task 5: Result parser and CSV merger

**Files:**
- Create: `pmo_analyzer/batch_collect.py`
- Create: `tests/pmo_analyzer/test_batch_collect.py`

- [ ] **Step 1: Write failing tests**

Create `tests/pmo_analyzer/test_batch_collect.py`:

```python
import pandas as pd
from unittest.mock import MagicMock

from pmo_analyzer.batch_collect import parse_result, merge_results

_ALL_COLS = ["pmo_score", "pmo_traj", "pmo_mat", "pmo_collab", "pmo_game", "pmo_feedback", "pmo_notes"]


def _make_success(custom_id: str, json_text: str) -> MagicMock:
    result = MagicMock()
    result.custom_id = custom_id
    result.result.type = "succeeded"
    block = MagicMock()
    block.type = "text"
    block.text = json_text
    result.result.message.content = [block]
    return result


def _make_errored(custom_id: str) -> MagicMock:
    result = MagicMock()
    result.custom_id = custom_id
    result.result.type = "errored"
    return result


def test_parse_result_extracts_all_five_sub_scores():
    raw = _make_success("1", '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"Good"}')
    parsed = parse_result(raw)
    assert parsed["pmo_traj"] == 8
    assert parsed["pmo_mat"] == 7
    assert parsed["pmo_collab"] == 5
    assert parsed["pmo_game"] == 6
    assert parsed["pmo_feedback"] == 9


def test_parse_result_calculates_pmo_score_as_average():
    raw = _make_success("1", '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"ok"}')
    parsed = parse_result(raw)
    assert parsed["pmo_score"] == round((8 + 7 + 5 + 6 + 9) / 5, 1)  # 7.0


def test_parse_result_preserves_notes():
    raw = _make_success("1", '{"traj":5,"mat":5,"collab":5,"game":5,"feedback":5,"notes":"Средний продукт"}')
    assert parse_result(raw)["pmo_notes"] == "Средний продукт"


def test_parse_result_returns_sentinel_on_invalid_json():
    raw = _make_success("1", "not valid {{ json")
    assert parse_result(raw)["pmo_score"] == -1.0


def test_parse_result_returns_sentinel_on_errored_result():
    assert parse_result(_make_errored("2"))["pmo_score"] == -1.0


def test_merge_results_adds_all_seven_new_columns():
    df = pd.DataFrame([{"id": 1, "name": "Co A"}, {"id": 2, "name": "Co B"}])
    results = {
        "1": {"pmo_score": 7.0, "pmo_traj": 7, "pmo_mat": 7, "pmo_collab": 7, "pmo_game": 7, "pmo_feedback": 7, "pmo_notes": "ok"},
        "2": {"pmo_score": -1.0, "pmo_traj": -1, "pmo_mat": -1, "pmo_collab": -1, "pmo_game": -1, "pmo_feedback": -1, "pmo_notes": "error"},
    }
    merged = merge_results(df, results)
    for col in _ALL_COLS:
        assert col in merged.columns, f"Missing column: {col}"


def test_merge_results_preserves_original_columns():
    df = pd.DataFrame([{"id": 1, "name": "Co A", "fund": "a16z", "sectors": "EdTech"}])
    results = {"1": {"pmo_score": 5.0, "pmo_traj": 5, "pmo_mat": 5, "pmo_collab": 5, "pmo_game": 5, "pmo_feedback": 5, "pmo_notes": "avg"}}
    merged = merge_results(df, results)
    assert merged.iloc[0]["fund"] == "a16z"
    assert merged.iloc[0]["sectors"] == "EdTech"


def test_merge_results_aligns_scores_to_correct_row():
    df = pd.DataFrame([{"id": 10, "name": "X"}, {"id": 20, "name": "Y"}])
    results = {
        "10": {"pmo_score": 9.0, "pmo_traj": 9, "pmo_mat": 9, "pmo_collab": 9, "pmo_game": 9, "pmo_feedback": 9, "pmo_notes": "great"},
        "20": {"pmo_score": 2.0, "pmo_traj": 2, "pmo_mat": 2, "pmo_collab": 2, "pmo_game": 2, "pmo_feedback": 2, "pmo_notes": "poor"},
    }
    merged = merge_results(df, results)
    assert merged.loc[merged["name"] == "X", "pmo_score"].iloc[0] == 9.0
    assert merged.loc[merged["name"] == "Y", "pmo_score"].iloc[0] == 2.0
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
pytest tests/pmo_analyzer/test_batch_collect.py -v
```

Expected: `ModuleNotFoundError: No module named 'pmo_analyzer.batch_collect'`

- [ ] **Step 3: Create pmo_analyzer/batch_collect.py**

```python
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
```

- [ ] **Step 4: Run the full test suite to confirm all tests pass**

```bash
pytest tests/pmo_analyzer/ -v
```

Expected: all tests pass (approximately 21 tests, 0 failures).

- [ ] **Step 5: Commit**

```bash
git add pmo_analyzer/batch_collect.py tests/pmo_analyzer/test_batch_collect.py
git commit -m "feat: add batch result parser and CSV merger with tests"
```

---

### Task 6: Run the full pipeline

**Prerequisite:** `ANTHROPIC_API_KEY` must be set.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

- [ ] **Step 1: Run scraper (~30 minutes)**

```bash
python -m pmo_analyzer.scraper
```

Expected output:
```
Scraping 3200 URLs (skipping 0 already done)...
Scraping websites: 100%|████████| 3200/3200 [28:14<00:00,  1.89it/s]
Saved 3200 entries to data/scraped.json
```

(~335 startups have no `website` field — these will rely on description only.)

- [ ] **Step 2: Verify scraped.json looks reasonable**

```bash
python -c "
import json
d = json.load(open('data/scraped.json'))
non_empty = sum(1 for v in d.values() if v)
print(f'{len(d)} entries, {non_empty} non-empty ({non_empty/len(d):.0%} success rate)')
"
```

Expected: something like `3200 entries, 1900 non-empty (59%)`. JS-heavy sites return empty strings — that's fine, the model falls back to description.

- [ ] **Step 3: Submit batch (~1 minute)**

```bash
python -m pmo_analyzer.batch_submit
```

Expected:
```
Submitting batch of 3535 requests...
Batch submitted: msgbatch_01AbCdEf...
Monitor: https://console.anthropic.com/batches/msgbatch_01AbCdEf...
```

- [ ] **Step 4: Collect results (~1 hour)**

```bash
python -m pmo_analyzer.batch_collect
```

Expected:
```
Polling batch msgbatch_01AbCdEf...
  processing — processing: 3200, waiting 60s...
  [... repeats until done ...]
Batch done — succeeded: 3510, errored: 25
Saved data/all_companies_pmo.csv: 3510/3535 scored, 25 errors
```

- [ ] **Step 5: Spot-check the results**

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/all_companies_pmo.csv')
print('Shape:', df.shape)
print('New columns:', list(df.columns[-7:]))
top = df[df['pmo_score'] >= 0].sort_values('pmo_score', ascending=False).head(10)
print(top[['name', 'fund', 'pmo_score', 'pmo_traj', 'pmo_mat', 'pmo_collab', 'pmo_game', 'pmo_feedback']].to_string())
"
```

Expected: table showing 10 highest-scoring startups with all 5 sub-scores filled in.
