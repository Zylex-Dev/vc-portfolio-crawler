# PMO Analyzer Redesign — Design Spec

**Date:** 2026-06-15
**Status:** Approved (pending user review)

## Goal

Simplify and improve `pmo_analyzer/` — the agent that scores each startup in
`data/all_companies.csv` on the 5 instruments of the Персонализированная Модель
Образования (PMO) framework and writes `data/all_companies_pmo.csv`.

Three drivers:

1. **Drop website scraping.** `data/scraped.json` is 99% empty (2159 of 2181
   entries blank), so the scraping pipeline adds cost and complexity for almost
   no signal.
2. **Upgrade the model.** Switch from `deepseek-v4-flash` (thinking disabled) to
   `deepseek-v4-pro` with reasoning enabled, matching `agent_matcher`, to improve
   scoring quality.
3. **Narrow the output.** A new run must update **only** `data/all_companies_pmo.csv`
   and touch no other data file.

## Scope decisions (confirmed with user)

- **Remove the Anthropic Claude batch path entirely** (`batch_submit.py`,
  `batch_collect.py`) and the scraper (`scraper.py`). Keep a single async
  DeepSeek scoring path mirroring `agent_matcher`.
- **Concurrency = 10** (matches `agent_matcher`; thinking mode is heavier than
  the previous flash run at 20).
- **`merge_results` lives in a new `pmo_analyzer/assemble.py`** for symmetry with
  `agent_matcher/assemble.py`.

## Target package layout

```
pmo_analyzer/
  __init__.py        # unchanged (empty)
  prompt.py          # build_system_prompt(), build_user_prompt(row)
  assemble.py        # merge_results(df, results) -> DataFrame
  scorer.py          # async scoring path + __main__ runner
```

Removed: `scraper.py`, `batch_submit.py`, `batch_collect.py`.

## Component design

### `prompt.py`

- `build_system_prompt()` — **unchanged.** The 5-instrument rubric (TRAJ, MAT,
  COLLAB, GAME, FEEDBACK; each 0–10) and the strict-JSON output contract
  `{"traj","mat","collab","game","feedback","notes"}` stay as-is.
- `build_user_prompt(row)` — **drop the `scraped_text` parameter** and the
  `Website content:` line. Renders: `Name`, `Sectors`, `Stage`, `Description`.
  Missing/None values render as `N/A` (existing behavior).

### `assemble.py`

- `merge_results(df: pd.DataFrame, results: dict[str, dict]) -> pd.DataFrame` —
  moved verbatim from the old `batch_collect.py`. Builds a score DataFrame keyed
  by integer `id` and left-merges it onto the input `df`.

### `scorer.py`

Constants:
- `MODEL = "deepseek-v4-pro"`
- `CONCURRENCY = 10`
- `MAX_TOKENS = 4096` (up from 256 — reasoning tokens must not crowd out the JSON
  answer; this is the lesson learned in `agent_matcher`)
- `_SENTINEL` unchanged (`pmo_score = -1.0`, all sub-scores `-1`, `pmo_notes` =
  `"error"` / `"parse_error"`).

Functions:
- `_parse_text(text)` — unchanged JSON parse → 5 ints + averaged `pmo_score`
  rounded to 1 decimal + `pmo_notes`; sentinel on failure.
- `score_one(row, client, system)` — **drops `scraped_text`**; calls
  `chat.completions.create` with `extra_body={"thinking": {"type": "enabled"}}`,
  `max_tokens=MAX_TOKENS`; broad `except` → sentinel copy.
- `score_all(df, ...)` — **drops the `scraped` argument**; builds the system
  prompt once, semaphore over `CONCURRENCY`, results keyed by `str(row["id"])`,
  tqdm over `asyncio.as_completed`. Imports `merge_results` from
  `pmo_analyzer.assemble`.

`__main__`:
- Reads `data/all_companies.csv` (2348 rows).
- Runs `score_all`, then `merge_results`.
- Writes **only** `data/all_companies_pmo.csv` (`index=False`, `encoding="utf-8"`).
- Prints `scored/total` and error count. No other file is written or modified.

## Data flow

```
data/all_companies.csv
   → score_all (per-row deepseek-v4-pro, thinking enabled, concurrency 10)
   → results dict keyed by id
   → merge_results(df, results)
   → data/all_companies_pmo.csv   (ONLY output)
```

## Error handling

- Per-row API failure or unparseable response → `_SENTINEL` row (`pmo_score=-1`),
  run continues. No retries (matches `agent_matcher`). Error rows are counted and
  reported at the end; `THRESHOLD`-style post-filtering is out of scope.

## Testing

- **Update** `tests/pmo_analyzer/test_prompt.py`: `build_user_prompt(row)` no
  longer takes `scraped_text`; assert it renders name/sectors/stage/description
  and no `Website content:` line.
- **Update** `tests/pmo_analyzer/test_scorer.py`: `score_one`/`score_all`
  signatures without `scraped`; mock `AsyncOpenAI`; verify `extra_body` carries
  `thinking: enabled` and `max_tokens=4096`; keep sentinel/parse-error coverage.
- **Add** a `merge_results` test (left-merge, id keying) in `test_scorer.py` or a
  new `test_assemble.py`.
- **Delete** `test_scraper.py`, `test_batch_submit.py`, `test_batch_collect.py`.
- No real network calls in tests (`AsyncMock`/`MagicMock`).
- Full repo suite must pass after the change.

## Git safety (executed before any code change)

Commit current versions of all data files so nothing is lost:
- `git add -f data/*.csv data/scraped.json` (and any other untracked `data/*`)
- Commit with a clear message (e.g. `chore: snapshot data files before pmo_analyzer redesign`).

## Out of scope

- No change to the scoring rubric or the meaning of the 5 instruments.
- No retries / backoff logic.
- No change to `agent_matcher`.
- No new output columns or files beyond the existing `all_companies_pmo.csv` schema.

## Cost note

A full run makes ~2348 real billable DeepSeek calls. The run is **not** executed
without explicit user authorization.
