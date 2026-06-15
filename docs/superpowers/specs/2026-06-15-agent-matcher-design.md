# Agent Matcher — дизайн

**Дата:** 2026-06-15
**Статус:** утверждён (брейншторм)

## Цель

Сопоставить EdTech-стартапы из `data/edu_companies_pmo.csv` (698 уникальных
стартапов) с каталогом из 44 ИИ-агентов (наших реализованных/планируемых решений),
сгруппированных по 5 средствам ПМО. Для каждого стартапа выбрать **один лучший
агент** либо отнести его в группу **unmatched** («новые идеи / решения, которых у
нас пока нет») для последующего анализа.

## Контекст и вводные

- **44 агента** в 5 файлах `data/agents/*.ts`: trajectory (11), materials (10),
  feedback (9), gamification (7), collaboration (7). Файлы импортируют
  несуществующий `../types` — это **data-only TS-литералы**, не компилируемый код.
  Node v20 доступен → стрипуем `import` и аннотацию `: AgentSpec[]`, eval'им в JSON.
- **698 уникальных стартапов** в `edu_companies_pmo.csv` (строк в файле больше из-за
  многострочных описаний).
- **`scraped.json` не используется** — совпадает лишь 3/698 slug (другое
  пространство имён). Матчинг опирается на CSV-поля `description` (в среднем 334
  символа, содержательные), `sectors` и 5 существующих под-оценок `pmo_*`.
- Переиспользуем проверенный паттерн `pmo_analyzer/`: async DeepSeek
  (OpenAI-совместимый клиент), semaphore-concurrency, sentinel при ошибке,
  merge → CSV.

## Решения (утверждены пользователем)

| Параметр | Значение |
|---|---|
| Кардинальность | Один лучший агент на стартап (либо unmatched) |
| Определение unmatched | Оценка relevance + порог (настраивается пост-фактум) |
| **Порог relevance** | **7** (жёсткий матч) |
| Выход | Оба файла: канонический assignment + агент-центричный пивот |
| **Модель** | **`deepseek-v4-pro`**, `thinking: {"type": "enabled"}` |
| **max_tokens** | **4096** (reasoning-токены + итоговый JSON) |
| Concurrency | 10 (pro+thinking медленнее/дороже; легко подкрутить) |

## Архитектура — модуль `agent_matcher/`

| Файл | Назначение |
|---|---|
| `agents_loader.py` | Через `subprocess`+node стрипует `import`/`: AgentSpec[]` из 5 `.ts`, eval'ит в JSON, кеширует в `data/agents/agents.json`. Присваивает `agent_id` 1–44 (детерминированно: порядок файлов traj→mat→feedback→game→collab, затем порядок внутри файла). |
| `prompt.py` | `build_system_prompt(catalog)`, `build_user_prompt(row)`. |
| `matcher.py` | `match_one` / `match_all` — зеркало `scorer.py`. |
| `assemble.py` | Из результатов строит 2 CSV. |
| `__init__.py` | — |

### Каталог агентов (system-промпт)

Компактный нумерованный список всех 44 агентов. На каждого:
`[<agent_id>] <средство> — <name>: <role>. <expectedBehavior>`.
Объём ~1800 токенов, кешируется как system-промпт между вызовами.

### Промпт стартапа (user-промпт)

`name`, `sectors`, `description`, плюс 5 под-оценок ПМО
(`pmo_traj/mat/collab/game/feedback`) как дополнительный сигнал.

### Контракт I/O (на стартап)

Модель отвечает строго JSON, без markdown-ограждений:
```json
{"agent_id": <int 1-44, или 0 если ничего не подходит>,
 "relevance": <int 0-10>,
 "rationale": "<одно предложение по-русски>"}
```
Числовой `agent_id` (а не имя) — чтобы модель не калечила кириллицу.
Невалидный/несуществующий id → трактуется как unmatched.

### Пороги и обработка ошибок

- `relevance < 7` ИЛИ `agent_id == 0` → группа **unmatched**.
- Ошибка API или парсинга → sentinel `agent_id = -1`, `relevance = -1` → группа
  **error** (перезапускаемо, как `_SENTINEL` в `scorer.py`).
- Порог вынесен в константу/параметр `assemble.py`, чтобы менять без перезапуска
  API (результаты модели сохраняются с сырым relevance).

## Выходные файлы

1. **`data/startup_agent_assignment.csv`** — канонический, 1 строка = 1 стартап:
   `id, name, fund, sectors, pmo_score, assigned_agent, agent_sredstvo,
   agent_status, relevance, rationale`.
   Ниже порога → `assigned_agent = "unmatched"`; ошибка → `"error"`.
2. **`data/agent_startups.csv`** — агент-центричный пивот, все 44 агента + строки
   `unmatched` и (при наличии) `error`:
   `agent_id, agent_name, sredstvo, developmentStatus, num_startups, startups`,
   где `startups` = `"Имя (relevance); Имя (relevance); …"` по убыванию relevance.

## Тестирование

Юнит-тесты в `tests/` (зеркало текущих конвенций: сетевой вызов не тестируется,
тестируются чистые функции):

- `agents_loader` — ровно 44 агента, уникальные `agent_id`, все поля на месте.
- `prompt` — каталог содержит все 44 id; user-промпт включает под-оценки.
- Парсинг ответа — валидный JSON; мусор/обрезка → sentinel.
- `assemble` — логика порога (6→unmatched, 7→matched), пивот, группы
  unmatched/error, сортировка startups по relevance.

## Запуск

`python -m agent_matcher.matcher` (мирроринг `pmo_analyzer.scorer`):
читает `edu_companies_pmo.csv` + `agents.json`, матчит, пишет оба CSV, печатает
сводку (matched / unmatched / error).

## Вне области (YAGNI)

- Two-stage routing по средствам, эмбеддинги, мульти-агентные назначения.
- Кеширование/инкрементальный перезапуск отдельных стартапов (полный прогон дёшев).
