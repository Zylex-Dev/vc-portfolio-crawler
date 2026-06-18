# ПМО · Карта рынка ИИ-агентов — интерактивный лендинг-отчёт

Статический отчёт-лендинг по исследованию: **518 EdTech-стартапов** из портфелей
**11 венчурных фондов**, сопоставленных с **44 ИИ-агентами** персонализированной
модели образования (ПМО). Показывает, где рынок уже строит то, что строим мы
(сматченные группы), и **232 стартапа «вне покрытия»** — зону новых продуктовых идей.

Реализация мокапа из Claude Design на полноценном фронтенд-стеке:
**Vite + React + TypeScript**. Собирается в статику и бесплатно деплоится на GitHub Pages.

## Стек

- **Vite 5** — сборка и dev-сервер
- **React 18 + TypeScript** — вся интерактивность (фильтры, сортировки, drawer, три вида)
- **Tailwind CSS v4** — оформление через утилиты + @theme-токены (CSS-first конфиг в index.css)
- **Python** (`scripts/build_data.py`) — конвертер исходных данных в `src/data/report.json`
- Шрифты: Newsreader (serif) + Hanken Grotesk (sans) — тёплая «бумажная» палитра

## Данные

Источник — артефакты исследования из `../data`:

| Файл | Назначение |
| --- | --- |
| `all_companies.csv` | 2348 собранных стартапов (даёт `totalCollected` для воронки) |
| `agents.json` | 44 ИИ-агента ПМО (название, средство, статус, роль, требования) |
| `startup_agent_assignment.csv` | 518 отфильтрованных EdTech-стартапов с pmo-метриками, релевантностью и привязкой к агенту |

Конвертер собирает их в один `src/data/report.json` вида
`{ meta, agents[], startups[] }`. Метрики (`pmo_score`, под-метрики, релевантность)
хранятся в исходной шкале **0–10**; ширина полос масштабируется в UI.

Перегенерировать данные (нужен Python 3):

```bash
npm run data        # = python3 scripts/build_data.py
```

`report.json` закоммичен в репозиторий, поэтому CI-сборке Python не требуется.

## Локальный запуск

```bash
npm install
npm run dev         # http://localhost:5173
```

## Сборка

```bash
npm run build       # tsc -b && vite build → dist/
npm run preview     # локальный просмотр собранной статики
```

## Деплой на GitHub Pages

Автоматически через GitHub Actions (`.github/workflows/deploy.yml` в корне репозитория):
любой push в `main`, затрагивающий `report-landing/**`, собирает и публикует `dist/`.

Один раз нужно включить Pages: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

`base` в `vite.config.ts` задан как `./` (относительные пути), поэтому сайт работает
по адресу `https://<user>.github.io/<repo>/` без привязки к имени репозитория.

## Структура

```
report-landing/
├─ index.html                    # точка входа + подключение шрифтов
├─ scripts/build_data.py          # CSV/JSON → src/data/report.json
├─ src/
│  ├─ main.tsx                   # монтирование React
│  ├─ App.tsx                    # корневой компонент, состояние, маршрутизация видов
│  ├─ types.ts                   # доменные типы
│  ├─ theme.ts                   # палитра C, статусы, форматирование
│  ├─ index.css                  # @theme-токены (palette, fonts, keyframes) + не-utility CSS
│  ├─ lib/
│  │  ├─ report.ts               # группировка стартапов по агентам + агрегаты
│  │  └─ text.ts                 # утилита clamp() для усечения строк
│  ├─ components/
│  │  ├─ Header.tsx              # шапка с лого и счётчиком фондов
│  │  ├─ Hero.tsx                # заголовок и блок 6 метрик
│  │  ├─ Controls.tsx            # тогл вида, чипы категорий, слайдер, поиск, сортировка
│  │  ├─ UnmatchedSection.tsx    # секция «232 стартапа вне покрытия»
│  │  ├─ Drawer.tsx              # боковая панель группы + карточки стартапов
│  │  ├─ AgentModal.tsx          # модальное окно с полными данными агента
│  │  ├─ shared.tsx              # переиспользуемые UI-элементы (StatusBadge и др.)
│  │  └─ views/
│  │     ├─ GridView.tsx         # вид «сетка» (карточки агентов)
│  │     ├─ CompactView.tsx      # вид «компактный» (таблица-строки)
│  │     └─ MapView.tsx          # вид «карта» (тайловая визуализация)
│  └─ data/report.json           # сгенерированные данные исследования
└─ vite.config.ts
```
