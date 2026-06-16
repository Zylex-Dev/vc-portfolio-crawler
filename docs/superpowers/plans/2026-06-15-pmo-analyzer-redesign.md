# PMO Analyzer Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify `pmo_analyzer/` to a single async DeepSeek scoring path on `deepseek-v4-pro` with reasoning enabled, dropping website scraping and the Anthropic batch path, writing only `data/all_companies_pmo.csv`.

**Architecture:** Three focused modules — `prompt.py` (prompt construction), `assemble.py` (merge scores into the source DataFrame), `scorer.py` (async per-row scoring + `__main__` runner). Mirrors the `agent_matcher` package. The scraper and Anthropic Claude batch path are removed entirely.

**Tech Stack:** Python, `pandas`, `openai.AsyncOpenAI` (DeepSeek base_url), `tqdm`, `python-dotenv`, `pytest` (`asyncio_mode=auto`), `unittest.mock`.

---

## File Structure

- `pmo_analyzer/prompt.py` — **modify**: `build_user_prompt(row)` loses the `scraped_text` param and the website line.
- `pmo_analyzer/assemble.py` — **create**: `merge_results(df, results)` (moved from `batch_collect.py`).
- `pmo_analyzer/scorer.py` — **modify**: model → `deepseek-v4-pro`, thinking enabled, `max_tokens=4096`, concurrency 10, drop `scraped`, import `merge_results` from `assemble`.
- `pmo_analyzer/scraper.py`, `batch_submit.py`, `batch_collect.py` — **delete**.
- `tests/pmo_analyzer/test_prompt.py` — **modify**: new `build_user_prompt(row)` signature.
- `tests/pmo_analyzer/test_scorer.py` — **modify**: new `score_one` signature, assert thinking/max_tokens.
- `tests/pmo_analyzer/test_assemble.py` — **create**: `merge_results` coverage.
- `tests/pmo_analyzer/test_scraper.py`, `test_batch_submit.py`, `test_batch_collect.py` — **delete**.
- `README.md` — **modify**: rewrite the pmo_analyzer run section (remove scraping step).
- `.gitignore` — **check**: leave `data/scraped.json` ignore entry harmless or remove if present.

---

### Task 0: Snapshot data files (git safety)

**Files:** none (git only)

- [ ] **Step 1: Stage all data files including currently-ignored ones**

```bash
git add -f data/ 2>/dev/null; true
```

This force-adds every file under `data/` (CSVs, `scraped.json`, `agents.json`, etc.), bypassing any `.gitignore` entry so the current versions are captured.

- [ ] **Step 2: Verify what is staged**

Run: `git status --short data/`
Expected: the data CSVs + `scraped.json` appear as staged (A/M). If a file does not exist, ignore it.

- [ ] **Step 3: Commit the snapshot**

```bash
git commit -m "chore: snapshot data files before pmo_analyzer redesign

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: commit succeeds. This preserves current data versions before regeneration.

---

### Task 1: Simplify `build_user_prompt` (drop scraped_text)

**Files:**
- Modify: `pmo_analyzer/prompt.py`
- Test: `tests/pmo_analyzer/test_prompt.py`

- [ ] **Step 1: Rewrite the prompt tests for the new signature**

Replace the entire contents of `tests/pmo_analyzer/test_prompt.py` with:

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
    result = build_user_prompt(row)
    assert "LearnAI" in result
    assert "AI;EdTech" in result
    assert "Seed" in result
    assert "Adaptive tutoring for kids." in result


def test_user_prompt_has_no_website_content_line():
    row = {"name": "Co", "sectors": "EdTech", "stage": "Seed", "description": "desc"}
    assert "Website content" not in build_user_prompt(row)


def test_user_prompt_shows_na_for_missing_row_keys():
    result = build_user_prompt({})
    assert result.count("N/A") >= 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/pmo_analyzer/test_prompt.py -v`
Expected: FAIL — `build_user_prompt` still requires the `scraped_text` argument (TypeError), and/or the website line still present.

- [ ] **Step 3: Update `build_user_prompt` in `pmo_analyzer/prompt.py`**

Replace the `build_user_prompt` function (keep `build_system_prompt` unchanged) with:

```python
def build_user_prompt(row: dict) -> str:
    return (
        f"Name: {row.get('name', 'N/A')}\n"
        f"Sectors: {row.get('sectors', 'N/A')}\n"
        f"Stage: {row.get('stage', 'N/A')}\n"
        f"Description: {row.get('description', 'N/A')}"
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/pmo_analyzer/test_prompt.py -v`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add pmo_analyzer/prompt.py tests/pmo_analyzer/test_prompt.py
git commit -m "refactor: drop scraped_text from pmo build_user_prompt

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Create `assemble.py` with `merge_results`

**Files:**
- Create: `pmo_analyzer/assemble.py`
- Test: `tests/pmo_analyzer/test_assemble.py`

- [ ] **Step 1: Write the failing test**

Create `tests/pmo_analyzer/test_assemble.py`:

```python
import pandas as pd

from pmo_analyzer.assemble import merge_results


def test_merge_results_joins_scores_on_id():
    df = pd.DataFrame([
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ])
    results = {
        "1": {"pmo_score": 7.0, "pmo_traj": 8, "pmo_mat": 7,
              "pmo_collab": 5, "pmo_game": 6, "pmo_feedback": 9, "pmo_notes": "ok"},
        "2": {"pmo_score": 4.0, "pmo_traj": 4, "pmo_mat": 4,
              "pmo_collab": 4, "pmo_game": 4, "pmo_feedback": 4, "pmo_notes": "meh"},
    }
    merged = merge_results(df, results)
    assert len(merged) == 2
    assert merged.loc[merged["id"] == 1, "pmo_score"].iloc[0] == 7.0
    assert merged.loc[merged["id"] == 2, "pmo_traj"].iloc[0] == 4
    assert "name" in merged.columns


def test_merge_results_left_join_keeps_unscored_rows():
    df = pd.DataFrame([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}])
    results = {
        "1": {"pmo_score": 7.0, "pmo_traj": 8, "pmo_mat": 7,
              "pmo_collab": 5, "pmo_game": 6, "pmo_feedback": 9, "pmo_notes": "ok"},
    }
    merged = merge_results(df, results)
    assert len(merged) == 2
    assert pd.isna(merged.loc[merged["id"] == 2, "pmo_score"].iloc[0])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/pmo_analyzer/test_assemble.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pmo_analyzer.assemble'`.

- [ ] **Step 3: Create `pmo_analyzer/assemble.py`**

```python
import pandas as pd


def merge_results(df: pd.DataFrame, results: dict[str, dict]) -> pd.DataFrame:
    rows = [{"id": int(k), **v} for k, v in results.items()]
    score_df = pd.DataFrame(rows)
    return df.merge(score_df, on="id", how="left")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/pmo_analyzer/test_assemble.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add pmo_analyzer/assemble.py tests/pmo_analyzer/test_assemble.py
git commit -m "feat: add pmo_analyzer assemble.merge_results

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Rewrite `scorer.py` (deepseek-v4-pro, thinking, no scraped)

**Files:**
- Modify: `pmo_analyzer/scorer.py`
- Test: `tests/pmo_analyzer/test_scorer.py`

- [ ] **Step 1: Rewrite the scorer tests for the new signature**

Replace the entire contents of `tests/pmo_analyzer/test_scorer.py` with:

```python
from unittest.mock import AsyncMock, MagicMock

from pmo_analyzer.scorer import MAX_TOKENS, MODEL, _parse_text, score_one


def test_parse_text_extracts_all_five_sub_scores():
    text = '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"Good"}'
    result = _parse_text(text)
    assert result["pmo_traj"] == 8
    assert result["pmo_mat"] == 7
    assert result["pmo_collab"] == 5
    assert result["pmo_game"] == 6
    assert result["pmo_feedback"] == 9


def test_parse_text_calculates_pmo_score_as_average():
    text = '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"ok"}'
    assert _parse_text(text)["pmo_score"] == round((8 + 7 + 5 + 6 + 9) / 5, 1)


def test_parse_text_preserves_notes():
    text = '{"traj":5,"mat":5,"collab":5,"game":5,"feedback":5,"notes":"Средний продукт"}'
    assert _parse_text(text)["pmo_notes"] == "Средний продукт"


def test_parse_text_returns_sentinel_on_invalid_json():
    assert _parse_text("not json {{")["pmo_score"] == -1.0


def test_parse_text_returns_sentinel_on_missing_score_key():
    assert _parse_text('{"traj":8,"mat":7,"notes":"incomplete"}')["pmo_score"] == -1.0


def test_model_is_deepseek_v4_pro():
    assert MODEL == "deepseek-v4-pro"
    assert MAX_TOKENS == 4096


async def test_score_one_returns_parsed_dict_on_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"ok"}'
    )
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await score_one(
        {"name": "TestCo", "sectors": "EdTech", "stage": "Seed", "description": "test"},
        mock_client,
        "system prompt",
    )
    assert result["pmo_traj"] == 8
    assert result["pmo_score"] == 7.0


async def test_score_one_enables_thinking_and_uses_max_tokens():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        '{"traj":1,"mat":1,"collab":1,"game":1,"feedback":1,"notes":"x"}'
    )
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    await score_one({"name": "X"}, mock_client, "system")

    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "deepseek-v4-pro"
    assert kwargs["max_tokens"] == 4096
    assert kwargs["extra_body"] == {"thinking": {"type": "enabled"}}


async def test_score_one_returns_sentinel_on_api_error():
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))

    result = await score_one({}, mock_client, "system")
    assert result["pmo_score"] == -1.0


async def test_score_one_returns_sentinel_on_invalid_response_json():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "I cannot score this startup."
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await score_one({}, mock_client, "system")
    assert result["pmo_score"] == -1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/pmo_analyzer/test_scorer.py -v`
Expected: FAIL — `score_one` still takes `scraped_text` (TypeError), `MAX_TOKENS` import missing, model is `deepseek-v4-flash`.

- [ ] **Step 3: Rewrite `pmo_analyzer/scorer.py`**

Replace the entire contents with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/pmo_analyzer/test_scorer.py -v`
Expected: PASS (10 tests).

- [ ] **Step 5: Commit**

```bash
git add pmo_analyzer/scorer.py tests/pmo_analyzer/test_scorer.py
git commit -m "feat: pmo scorer on deepseek-v4-pro with thinking, drop scraped

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Delete scraper + Anthropic batch path and their tests

**Files:**
- Delete: `pmo_analyzer/scraper.py`, `pmo_analyzer/batch_submit.py`, `pmo_analyzer/batch_collect.py`
- Delete: `tests/pmo_analyzer/test_scraper.py`, `tests/pmo_analyzer/test_batch_submit.py`, `tests/pmo_analyzer/test_batch_collect.py`

- [ ] **Step 1: Remove the source and test files**

```bash
git rm pmo_analyzer/scraper.py pmo_analyzer/batch_submit.py pmo_analyzer/batch_collect.py \
       tests/pmo_analyzer/test_scraper.py tests/pmo_analyzer/test_batch_submit.py \
       tests/pmo_analyzer/test_batch_collect.py
```

- [ ] **Step 2: Verify no remaining imports reference the deleted modules**

Run: `grep -rn "batch_collect\|batch_submit\|pmo_analyzer.scraper\|from pmo_analyzer import scraper" pmo_analyzer/ tests/ agent_matcher/`
Expected: no output (empty). If anything prints, fix that import before continuing.

- [ ] **Step 3: Run the full pmo_analyzer test suite**

Run: `.venv/bin/pytest tests/pmo_analyzer/ -v`
Expected: PASS — only `test_prompt.py`, `test_scorer.py`, `test_assemble.py` collected; no import errors.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove scraper and Anthropic batch path from pmo_analyzer

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Update README (remove scraping step)

**Files:**
- Modify: `README.md` (the pmo_analyzer run section, around lines 199–227)

- [ ] **Step 1: Replace the "Step 1 — Scrape" + "Step 2 — Score" block**

In `README.md`, replace this block:

```markdown
### Step 1 — Scrape startup websites (~30 min)

```bash
.venv/bin/python -m pmo_analyzer.scraper
```

Reads `data/all_companies.csv`, async-scrapes up to 3000 chars from each startup's website, saves to `data/scraped.json`. Idempotent — safe to restart if interrupted.

### Step 2 — Score all startups (~20 min)

```bash
.venv/bin/python -m pmo_analyzer.scorer
```

Sends one prompt per startup (description + sectors + stage + scraped text) to DeepSeek concurrently, merges scores into the original CSV, saves `data/all_companies_pmo.csv`.
```

with:

```markdown
### Score all startups

```bash
.venv/bin/python -m pmo_analyzer.scorer
```

Reads `data/all_companies.csv` and sends one prompt per startup (name + sectors + stage + description) to `deepseek-v4-pro` (reasoning enabled) concurrently, merges the scores into the source rows, and writes **only** `data/all_companies_pmo.csv`.
```

- [ ] **Step 2: Fix the trailing error-row note**

In `README.md`, replace:

```markdown
Rows with `pmo_score == -1` are batch errors — retry or review manually.
```

with:

```markdown
Rows with `pmo_score == -1` are API/parse errors — re-run or review manually.
```

- [ ] **Step 3: Verify no stale scraper references remain**

Run: `grep -n -i "scrap" README.md`
Expected: no output (empty).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update pmo_analyzer run instructions (no scraping)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Full suite verification

**Files:** none

- [ ] **Step 1: Run the entire repo test suite**

Run: `.venv/bin/pytest -q`
Expected: PASS — all tests green, no collection/import errors. (Suite size drops by the 3 deleted test files.)

- [ ] **Step 2: Confirm the package imports cleanly**

Run: `.venv/bin/python -c "import pmo_analyzer.scorer, pmo_analyzer.assemble, pmo_analyzer.prompt; print('ok')"`
Expected: `ok`

---

### Task 7: Billable run — score all startups (REQUIRES EXPLICIT USER GO-AHEAD)

> **Do NOT execute without the user explicitly authorizing the run.** This makes ~2348 real DeepSeek calls.

- [ ] **Step 1 (optional): Smoke test on 3 rows**

```bash
.venv/bin/python -c "
import asyncio, pandas as pd
from pmo_analyzer.scorer import score_all
from pmo_analyzer.assemble import merge_results
df = pd.read_csv('data/all_companies.csv').head(3)
res = asyncio.run(score_all(df))
print(merge_results(df, res)[['name','pmo_score','pmo_traj','pmo_notes']].to_string())
"
```

Expected: 3 rows with `pmo_score` in 0–10 (not -1). If all -1, inspect a raw response before the full run (likely max_tokens or thinking field).

- [ ] **Step 2: Full run**

```bash
.venv/bin/python -m pmo_analyzer.scorer
```

Expected: progress bar over 2348 rows; final line `Saved data/all_companies_pmo.csv: <scored>/2348 scored, <errors> errors`. Only `data/all_companies_pmo.csv` is written.

- [ ] **Step 3: Commit the regenerated output**

```bash
git add data/all_companies_pmo.csv
git commit -m "data: regenerate all_companies_pmo.csv with deepseek-v4-pro

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review notes

- **Spec coverage:** drop scraped.json (Task 1, 4), deepseek-v4-pro + thinking (Task 3), max_tokens 4096 (Task 3), concurrency 10 (Task 3), merge_results in assemble.py (Task 2), output only all_companies_pmo.csv (Task 3 `__main__`), remove batch+scraper (Task 4), git snapshot first (Task 0), README (Task 5), billable run gated (Task 7). All covered.
- **Type consistency:** `score_one(row, client, system)`, `score_all(df)`, `merge_results(df, results)`, `build_user_prompt(row)`, `build_system_prompt()` consistent across tasks and tests.
- **No placeholders:** every code/test step shows full content.
