# Agent Matcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Сопоставить 698 EdTech-стартапов из `data/edu_companies_pmo.csv` с каталогом из 44 ИИ-агентов, назначив каждому стартапу один лучший агент (relevance ≥ 7) либо группу `unmatched`, и выгрузить два CSV.

**Architecture:** Новый модуль `agent_matcher/`, зеркалящий проверенный паттерн `pmo_analyzer/` (async OpenAI-совместимый клиент DeepSeek, semaphore-concurrency, sentinel при ошибках, merge → CSV). Агенты загружаются из `.ts`-литералов через node-eval в кешируемый `data/agents/agents.json`. На каждый стартап — один вызов `deepseek-v4-pro` с включённым thinking; в system-промпте нумерованный каталог всех 44 агентов; модель возвращает `agent_id` + `relevance` + `rationale`. Порог применяется пост-фактум при сборке CSV.

**Tech Stack:** Python 3, `openai` (AsyncOpenAI), `pandas`, `tqdm`, `python-dotenv`, `pytest`/`pytest-asyncio` (`asyncio_mode=auto`), Node v20 (для парсинга `.ts`).

---

## File Structure

| Файл | Ответственность |
|---|---|
| `agent_matcher/__init__.py` | Маркер пакета. |
| `agent_matcher/agents_loader.py` | node-eval `.ts` → `agents.json`, присвоение `agent_id` 1–44, загрузка/кеш. |
| `agent_matcher/prompt.py` | `build_system_prompt(agents)`, `build_user_prompt(row)`. |
| `agent_matcher/matcher.py` | `_parse_response`, `match_one`, `match_all`, `__main__`-раннер. |
| `agent_matcher/assemble.py` | `build_assignment_df`, `build_agent_pivot_df`, `THRESHOLD`. |
| `tests/agent_matcher/__init__.py` | Маркер тест-пакета. |
| `tests/agent_matcher/test_agents_loader.py` | Тесты загрузчика (на реальных `.ts`). |
| `tests/agent_matcher/test_prompt.py` | Тесты промптов. |
| `tests/agent_matcher/test_matcher.py` | Тесты парсинга и `match_one` (мок-клиент). |
| `tests/agent_matcher/test_assemble.py` | Тесты порога, групп, пивота. |

---

## Task 1: Package scaffolding + agents loader

**Files:**
- Create: `agent_matcher/__init__.py`
- Create: `tests/agent_matcher/__init__.py`
- Create: `agent_matcher/agents_loader.py`
- Test: `tests/agent_matcher/test_agents_loader.py`

- [ ] **Step 1: Create empty package markers**

```bash
mkdir -p agent_matcher tests/agent_matcher
touch agent_matcher/__init__.py tests/agent_matcher/__init__.py
```

- [ ] **Step 2: Write the failing test**

Create `tests/agent_matcher/test_agents_loader.py`:

```python
from agent_matcher.agents_loader import load_agents


def test_loads_exactly_44_agents():
    agents = load_agents(force_rebuild=True)
    assert len(agents) == 44


def test_agent_ids_are_sequential_1_to_44():
    ids = [a["agent_id"] for a in load_agents()]
    assert ids == list(range(1, 45))


def test_each_agent_has_required_fields():
    for a in load_agents():
        for field in ("name", "sredstvo", "role", "expectedBehavior", "developmentStatus"):
            assert field in a, f"missing {field}"
            assert a[field] is not None, f"null {field}"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/agent_matcher/test_agents_loader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agent_matcher.agents_loader'`

- [ ] **Step 4: Write the implementation**

Create `agent_matcher/agents_loader.py`:

```python
import json
import re
import subprocess
import tempfile
from pathlib import Path

AGENTS_DIR = Path("data/agents")
CACHE_PATH = AGENTS_DIR / "agents.json"
# Порядок файлов фиксирует диапазоны agent_id (1-44).
FILE_ORDER = ["trajectory", "materials", "feedback", "gamification", "collaboration"]

_IMPORT_RE = re.compile(r"^\s*import\b.*$", re.MULTILINE)
_EXPORT_RE = re.compile(r"export\s+const\s+\w+\s*:\s*AgentSpec\[\]\s*=")


def _ts_to_objects(ts_path: Path) -> list[dict]:
    """Strip TS-only syntax and eval the array literal via node into JSON."""
    src = ts_path.read_text(encoding="utf-8")
    src = _IMPORT_RE.sub("", src)
    src = _EXPORT_RE.sub("module.exports =", src, count=1)
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False, encoding="utf-8") as f:
        f.write(src)
        tmp = f.name
    try:
        completed = subprocess.run(
            ["node", "-e", f"process.stdout.write(JSON.stringify(require({json.dumps(tmp)})))"],
            capture_output=True,
            text=True,
            check=True,
        )
    finally:
        Path(tmp).unlink(missing_ok=True)
    return json.loads(completed.stdout)


def build_agents_json() -> list[dict]:
    agents: list[dict] = []
    agent_id = 1
    for stem in FILE_ORDER:
        for obj in _ts_to_objects(AGENTS_DIR / f"{stem}.ts"):
            obj["agent_id"] = agent_id
            agents.append(obj)
            agent_id += 1
    CACHE_PATH.write_text(json.dumps(agents, ensure_ascii=False, indent=2), encoding="utf-8")
    return agents


def load_agents(force_rebuild: bool = False) -> list[dict]:
    if force_rebuild or not CACHE_PATH.exists():
        return build_agents_json()
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/agent_matcher/test_agents_loader.py -v`
Expected: PASS (3 tests). Side effect: `data/agents/agents.json` created.

- [ ] **Step 6: Commit**

```bash
git add agent_matcher/__init__.py agent_matcher/agents_loader.py tests/agent_matcher/__init__.py tests/agent_matcher/test_agents_loader.py data/agents/agents.json
git commit -m "feat: add agent_matcher agents loader (ts->json via node-eval)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Prompt builders

**Files:**
- Create: `agent_matcher/prompt.py`
- Test: `tests/agent_matcher/test_prompt.py`

- [ ] **Step 1: Write the failing test**

Create `tests/agent_matcher/test_prompt.py`:

```python
from agent_matcher.prompt import build_system_prompt, build_user_prompt

AGENTS = [
    {"agent_id": 1, "sredstvo": "Геймификация", "name": "Метаучебник",
     "role": "Карта знаний", "expectedBehavior": "Ученик видит карту"},
    {"agent_id": 2, "sredstvo": "Материалы", "name": "Генератор",
     "role": "Создаёт контент", "expectedBehavior": "Учитель генерирует"},
]


def test_system_prompt_lists_all_agent_ids_and_names():
    p = build_system_prompt(AGENTS)
    assert "[1]" in p and "[2]" in p
    assert "Метаучебник" in p and "Генератор" in p


def test_system_prompt_requests_json_with_agent_id():
    p = build_system_prompt(AGENTS)
    assert "JSON" in p
    assert "agent_id" in p
    assert "relevance" in p


def test_user_prompt_includes_startup_fields_and_pmo_scores():
    row = {
        "name": "LearnAI", "sectors": "AI;EdTech", "description": "Adaptive tutoring",
        "pmo_traj": 8, "pmo_mat": 7, "pmo_collab": 5, "pmo_game": 6, "pmo_feedback": 9,
    }
    r = build_user_prompt(row)
    assert "LearnAI" in r
    assert "AI;EdTech" in r
    assert "Adaptive tutoring" in r
    assert "8" in r and "9" in r


def test_user_prompt_shows_na_for_missing_fields():
    assert "N/A" in build_user_prompt({})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agent_matcher/test_prompt.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agent_matcher.prompt'`

- [ ] **Step 3: Write the implementation**

Create `agent_matcher/prompt.py`:

```python
def build_system_prompt(agents: list[dict]) -> str:
    catalog = "\n".join(
        f"[{a['agent_id']}] {a['sredstvo']} — {a['name']}: {a['role']}. {a['expectedBehavior']}"
        for a in agents
    )
    return (
        "Ты — эксперт по EdTech и образовательным технологиям. У нас есть каталог из "
        "44 ИИ-агентов (наших решений), сгруппированных по 5 средствам ПМО "
        "(Персонализированная Модель Образования). Тебе дают описание стартапа. "
        "Выбери ОДНОГО агента из каталога, к которому стартап ближе всего по сути и "
        "назначению. Если стартап не подходит ни к одному агенту — верни agent_id 0.\n\n"
        f"КАТАЛОГ АГЕНТОВ:\n{catalog}\n\n"
        "Оцени релевантность лучшего совпадения по шкале 0–10, где 10 — стартап делает "
        "ровно то же, что агент, а 0 — совпадения нет.\n\n"
        "Ответь СТРОГО валидным JSON без markdown-ограждений:\n"
        '{"agent_id": <int 1-44 или 0>, "relevance": <int 0-10>, '
        '"rationale": "<одно предложение по-русски>"}'
    )


def build_user_prompt(row: dict) -> str:
    def g(key: str) -> str:
        value = row.get(key)
        return str(value) if value not in (None, "") else "N/A"

    return (
        f"Название: {g('name')}\n"
        f"Сектора: {g('sectors')}\n"
        f"Описание: {g('description')}\n"
        f"Оценки ПМО (0-10) — траектория: {g('pmo_traj')}, материалы: {g('pmo_mat')}, "
        f"совместность: {g('pmo_collab')}, геймификация: {g('pmo_game')}, "
        f"обратная связь: {g('pmo_feedback')}"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agent_matcher/test_prompt.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add agent_matcher/prompt.py tests/agent_matcher/test_prompt.py
git commit -m "feat: add agent_matcher prompt builders

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Matcher (parse + async calls)

**Files:**
- Create: `agent_matcher/matcher.py`
- Test: `tests/agent_matcher/test_matcher.py`

- [ ] **Step 1: Write the failing test**

Create `tests/agent_matcher/test_matcher.py`:

```python
from unittest.mock import AsyncMock, MagicMock

from agent_matcher.matcher import _parse_response, match_one


def test_parse_response_extracts_fields():
    r = _parse_response('{"agent_id": 5, "relevance": 8, "rationale": "Подходит"}')
    assert r["agent_id"] == 5
    assert r["relevance"] == 8
    assert r["rationale"] == "Подходит"


def test_parse_response_handles_markdown_fences_and_noise():
    r = _parse_response('Вот ответ:\n```json\n{"agent_id": 3, "relevance": 7, "rationale": "ok"}\n```')
    assert r["agent_id"] == 3
    assert r["relevance"] == 7


def test_parse_response_sentinel_on_invalid_json():
    assert _parse_response("not json at all")["agent_id"] == -1


def test_parse_response_sentinel_on_missing_key():
    r = _parse_response('{"relevance": 8, "rationale": "no id"}')
    assert r["agent_id"] == -1
    assert r["rationale"] == "parse_error"


async def test_match_one_returns_parsed_dict_on_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        '{"agent_id": 4, "relevance": 9, "rationale": "ok"}'
    )
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    r = await match_one({"name": "TestCo"}, mock_client, "system prompt")
    assert r["agent_id"] == 4
    assert r["relevance"] == 9


async def test_match_one_returns_sentinel_on_api_error():
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))

    r = await match_one({}, mock_client, "system")
    assert r["agent_id"] == -1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agent_matcher/test_matcher.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agent_matcher.matcher'`

- [ ] **Step 3: Write the implementation**

Create `agent_matcher/matcher.py`:

```python
import asyncio
import json
import os
from pathlib import Path

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
```

NOTE: `matcher.py` imports `assemble` (Task 4). The unit tests in this task only touch `_parse_response` and `match_one`, but the import is resolved at module load. Implement Task 4 before running `python -m agent_matcher.matcher`. The pytest run in Step 4 still works only after Task 4 exists — so run Step 4 now expecting the import error, then re-run after Task 4. To keep this task self-contained, Step 4 below tolerates that ordering.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agent_matcher/test_matcher.py -v`
Expected: If Task 4 not yet done → collection error `ModuleNotFoundError: agent_matcher.assemble`. In that case proceed to Task 4, then re-run: PASS (6 tests). If you prefer strict ordering, do Task 4 first.

- [ ] **Step 5: Commit**

```bash
git add agent_matcher/matcher.py tests/agent_matcher/test_matcher.py
git commit -m "feat: add agent_matcher async matcher (deepseek-v4-pro, thinking)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Assemble output CSVs

**Files:**
- Create: `agent_matcher/assemble.py`
- Test: `tests/agent_matcher/test_assemble.py`

- [ ] **Step 1: Write the failing test**

Create `tests/agent_matcher/test_assemble.py`:

```python
import pandas as pd

from agent_matcher.assemble import build_agent_pivot_df, build_assignment_df

AGENTS = [
    {"agent_id": 1, "name": "Метаучебник", "sredstvo": "Геймификация",
     "developmentStatus": "Протестировать", "role": "r", "expectedBehavior": "e"},
    {"agent_id": 2, "name": "Генератор", "sredstvo": "Материалы",
     "developmentStatus": "В разработке", "role": "r", "expectedBehavior": "e"},
]


def _df():
    return pd.DataFrame([
        {"id": 10, "name": "A", "fund": "f", "sectors": "EdTech", "pmo_score": 5.0},
        {"id": 11, "name": "B", "fund": "f", "sectors": "EdTech", "pmo_score": 6.0},
        {"id": 12, "name": "C", "fund": "f", "sectors": "EdTech", "pmo_score": 7.0},
        {"id": 13, "name": "D", "fund": "f", "sectors": "EdTech", "pmo_score": 3.0},
    ])


def _results():
    return {
        "10": {"agent_id": 1, "relevance": 9, "rationale": "strong"},
        "11": {"agent_id": 1, "relevance": 6, "rationale": "weak"},    # < threshold -> unmatched
        "12": {"agent_id": 0, "relevance": 0, "rationale": "none"},    # explicit none -> unmatched
        "13": {"agent_id": -1, "relevance": -1, "rationale": "error"}, # error
    }


def test_assignment_threshold_and_groups():
    a = build_assignment_df(_df(), _results(), AGENTS, threshold=7)
    byid = {int(r["id"]): r for _, r in a.iterrows()}
    assert byid[10]["assigned_agent"] == "Метаучебник"
    assert byid[10]["agent_sredstvo"] == "Геймификация"
    assert byid[11]["assigned_agent"] == "unmatched"
    assert byid[12]["assigned_agent"] == "unmatched"
    assert byid[13]["assigned_agent"] == "error"


def test_assignment_invalid_agent_id_is_unmatched():
    res = {"10": {"agent_id": 999, "relevance": 10, "rationale": "x"}}
    df = pd.DataFrame([{"id": 10, "name": "A", "fund": "f", "sectors": "EdTech", "pmo_score": 5.0}])
    a = build_assignment_df(df, res, AGENTS)
    assert a.iloc[0]["assigned_agent"] == "unmatched"


def test_pivot_has_all_agents_plus_unmatched_and_error():
    a = build_assignment_df(_df(), _results(), AGENTS, threshold=7)
    p = build_agent_pivot_df(a, AGENTS)
    names = list(p["agent_name"])
    assert "Метаучебник" in names
    assert "Генератор" in names          # ноль стартапов, но строка присутствует
    assert "unmatched" in names
    assert "error" in names
    meta = p[p["agent_name"] == "Метаучебник"].iloc[0]
    assert meta["num_startups"] == 1
    assert "A (9)" in meta["startups"]
    genr = p[p["agent_name"] == "Генератор"].iloc[0]
    assert genr["num_startups"] == 0


def test_pivot_sorts_startups_by_relevance_desc():
    df = pd.DataFrame([
        {"id": 1, "name": "Low", "fund": "f", "sectors": "e", "pmo_score": 1},
        {"id": 2, "name": "High", "fund": "f", "sectors": "e", "pmo_score": 1},
    ])
    res = {
        "1": {"agent_id": 1, "relevance": 7, "rationale": ""},
        "2": {"agent_id": 1, "relevance": 10, "rationale": ""},
    }
    a = build_assignment_df(df, res, AGENTS)
    s = build_agent_pivot_df(a, AGENTS)
    row = s[s["agent_name"] == "Метаучебник"].iloc[0]["startups"]
    assert row.index("High") < row.index("Low")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/agent_matcher/test_assemble.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'agent_matcher.assemble'`

- [ ] **Step 3: Write the implementation**

Create `agent_matcher/assemble.py`:

```python
import pandas as pd

THRESHOLD = 7


def build_assignment_df(
    df: pd.DataFrame,
    results: dict[str, dict],
    agents: list[dict],
    threshold: int = THRESHOLD,
) -> pd.DataFrame:
    by_id = {a["agent_id"]: a for a in agents}
    rows = []
    for _, r in df.iterrows():
        res = results.get(
            str(r["id"]), {"agent_id": -1, "relevance": -1, "rationale": "missing"}
        )
        aid = res["agent_id"]
        rel = res["relevance"]

        if aid == -1:
            assigned, sredstvo, status = "error", "", ""
        elif aid == 0 or aid not in by_id or rel < threshold:
            assigned, sredstvo, status = "unmatched", "", ""
        else:
            agent = by_id[aid]
            assigned = agent["name"]
            sredstvo = agent["sredstvo"]
            status = agent.get("developmentStatus", "")

        rows.append({
            "id": int(r["id"]),
            "name": r.get("name"),
            "fund": r.get("fund"),
            "sectors": r.get("sectors"),
            "pmo_score": r.get("pmo_score"),
            "assigned_agent": assigned,
            "agent_sredstvo": sredstvo,
            "agent_status": status,
            "relevance": rel,
            "rationale": res.get("rationale", ""),
        })
    return pd.DataFrame(rows)


def _format_startups(sub: pd.DataFrame) -> str:
    sub = sub.sort_values("relevance", ascending=False)
    return "; ".join(
        f"{name} ({int(rel)})" for name, rel in zip(sub["name"], sub["relevance"])
    )


def build_agent_pivot_df(assignment: pd.DataFrame, agents: list[dict]) -> pd.DataFrame:
    rows = []
    for a in agents:
        sub = assignment[assignment["assigned_agent"] == a["name"]]
        rows.append({
            "agent_id": a["agent_id"],
            "agent_name": a["name"],
            "sredstvo": a["sredstvo"],
            "developmentStatus": a.get("developmentStatus", ""),
            "num_startups": len(sub),
            "startups": _format_startups(sub),
        })
    for group in ("unmatched", "error"):
        sub = assignment[assignment["assigned_agent"] == group]
        rows.append({
            "agent_id": "",
            "agent_name": group,
            "sredstvo": "",
            "developmentStatus": "",
            "num_startups": len(sub),
            "startups": _format_startups(sub),
        })
    return pd.DataFrame(rows)
```

NOTE: pivot always emits `unmatched` and `error` rows (zero count if empty) — keeps the schema stable and the test deterministic.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agent_matcher/test_assemble.py tests/agent_matcher/test_matcher.py -v`
Expected: PASS (4 assemble + 6 matcher = 10 tests). Running both confirms Task 3's import of `assemble` now resolves.

- [ ] **Step 5: Commit**

```bash
git add agent_matcher/assemble.py tests/agent_matcher/test_assemble.py
git commit -m "feat: add agent_matcher CSV assembly (assignment + agent pivot)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Full-suite check + smoke run

**Files:** none (verification only)

- [ ] **Step 1: Run the whole agent_matcher suite**

Run: `pytest tests/agent_matcher/ -v`
Expected: PASS (3 + 4 + 6 + 4 = 17 tests).

- [ ] **Step 2: Confirm the runner wiring imports cleanly (no API call)**

Run: `python -c "import agent_matcher.matcher; print('ok', agent_matcher.matcher.MODEL)"`
Expected: `ok deepseek-v4-pro`

- [ ] **Step 3: Smoke-test the runner on a 3-row sample (real API)**

This makes 3 real DeepSeek calls — confirms the response shape (thinking + JSON in `message.content`) and that `max_tokens=4096` is enough before the full 698-row run.

Run:
```bash
python -c "
import asyncio, pandas as pd
from agent_matcher.agents_loader import load_agents
from agent_matcher.matcher import match_all
from agent_matcher.assemble import build_assignment_df, build_agent_pivot_df
df = pd.read_csv('data/edu_companies_pmo.csv').head(3)
agents = load_agents()
res = asyncio.run(match_all(df, agents))
print(build_assignment_df(df, res, agents)[['name','assigned_agent','relevance']].to_string())
"
```
Expected: 3 rows printed, `relevance` values in 0–10 (not -1). If you see `relevance=-1` for all, inspect a raw response — likely `max_tokens` too low or `thinking` field name; fix before full run.

- [ ] **Step 4: Full run**

Run: `python -m agent_matcher.matcher`
Expected: tqdm progress over 698 startups, then `Saved. matched=…, unmatched=…, errors=…`. Produces `data/startup_agent_assignment.csv` and `data/agent_startups.csv`.

- [ ] **Step 5: Commit outputs**

```bash
git add data/startup_agent_assignment.csv data/agent_startups.csv
git commit -m "data: agent-matching results for 698 EdTech startups

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review notes

- **Spec coverage:** loader (Task 1) ↔ agents.json/44/node-eval; prompt (Task 2) ↔ catalog + I/O contract; matcher (Task 3) ↔ deepseek-v4-pro/thinking/max_tokens=4096/concurrency=10/sentinel; assemble (Task 4) ↔ threshold=7/two CSVs/unmatched+error groups; runner+smoke (Task 5) ↔ run entry + validation. All spec sections mapped.
- **Type consistency:** result dict keys `agent_id`/`relevance`/`rationale` consistent across matcher↔assemble; sentinel `agent_id=-1` consistent; `by_id` keyed by int `agent_id` matches loader's int assignment; CSV columns match spec.
- **Ordering caveat** for Task 3↔4 import is called out explicitly in both tasks.
