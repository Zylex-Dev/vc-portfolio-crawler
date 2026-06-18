# Report-Landing — код-ревью + миграция на Tailwind CSS — дизайн

**Дата:** 2026-06-18
**Статус:** утверждён (брейншторм)
**Область:** только `report-landing/` (веб-лендинг). Остальной проект не трогаем.

## Цель

Провести код-ревью модуля `report-landing/`, выполнить структурный
рефакторинг и перевести всё оформление с inline-стилей (`style={{}}`) на
**Tailwind CSS v4**. Рендер страницы должен остаться **пиксель-в-пиксель**
идентичным текущему.

## Контекст (результаты ревью)

Стек: Vite 5 + React 18 + TypeScript. Данные — статический `src/data/report.json`,
чистый слой `lib/report.ts` + `types.ts` (нарекания отсутствуют, **не трогаем**).

**Что хорошо:** централизованная палитра в `theme.ts`; доступность
(`role="dialog"`, `aria-modal`, `aria-label`, `:focus-visible`,
`prefers-reduced-motion`).

**Что чиним по ходу миграции:**

1. **~95% оформления — inline `style={{}}`.** Многословно, не переиспользуется,
   нет адаптива, магические числа (`fontSize: 12.5/13.5`) и десятки разовых
   hex-цветов вне палитры `C` (`#3F7D55`, `#6B5E4D`, `#EFE6D6`, `#EBDCC9`…).
2. **`App.tsx` ~460 строк** — в одном файле `App` + `LegendItem` + `GridView` +
   `CompactView` + `MapView` + `UnmatchedSection` + хелпер.
3. **Дублирование `clamp`/`clampText`** — в `App.tsx` и `Drawer.tsx`.
4. **Мёртвый код в `shared.tsx`:** `Bar` и `pill` экспортируются, но нигде не
   используются (подтверждено grep). `FONT_SANS` в `theme.ts` — тоже мёртвый.

## Решения (утверждены пользователем)

| Параметр | Значение |
|---|---|
| Версия Tailwind | **v4** (CSS-first `@theme`, без JS-конфига, плагин `@tailwindcss/vite`) |
| Точность визуала | **Пиксель-в-пиксель** (arbitrary values `text-[12.5px]`, точные токены палитры) |
| Объём рефактора | **Конвертация + структурная чистка** (разбить вьюхи, общий `clamp`, удалить мёртвый код) |

## Архитектура решения

### 1. Подключение Tailwind v4

- `npm i -D tailwindcss @tailwindcss/vite`
- `vite.config.ts`: добавить плагин `tailwindcss()` в `plugins`.
- `src/index.css`: `@import "tailwindcss";` + блок `@theme { … }` с токенами.
- Кастомный CSS, который Tailwind утилитами не выразить (трек/ползунок
  `input[type=range]`, скроллбар `::-webkit-scrollbar`, `::selection`,
  keyframes `fadeUp`/`fadeIn`), **остаётся** в `index.css`. Хук-классы
  (`.agent-card:hover` и т.д.) переезжают в утилиты на самих элементах
  (`hover:`, `focus-visible:`), кроме того, что нельзя выразить классами.

### 2. Дизайн-токены в `@theme`

Палитра `C` из `theme.ts` → CSS-переменные Tailwind, плюс одноразовые цвета,
встречающиеся в коде. Примеры (имена — kebab под `--color-*`):

```css
@theme {
  --color-paper: #F4EEE4;  --color-card: #FBF8F2;  --color-card-alt: #F7F1E7;
  --color-border: #E7DECF; --color-border-warm: #EBE2D2;
  --color-ink: #211C16;    --color-ink-soft: #5C5345;
  --color-muted: #837A6C;  --color-faint: #A9997F;  --color-track: #EDE3D3;
  --color-clay: #C2603C;   --color-clay-deep: #A6431F; --color-teal: #3F8A78;
  /* статусные и разовые: prod-green #3F7D55, dev-amber #A9781F, prose #6B5E4D … */
  --font-serif: "Newsreader", serif;
  --font-sans: "Hanken Grotesk", system-ui, sans-serif;
}
```

Это даёт классы вида `bg-paper text-ink border-border font-serif`.
`theme.ts` сохраняет объект `C` и `statusMeta()` — они нужны там, где цвет
вычисляется в рантайме (статус-бейджи, плитки карты), и для значений,
передаваемых в `style` динамически (ширина полос `barW`). То есть палитра
живёт в **одном** источнике концептуально, но физически дублируется в `@theme`
(для статичных классов) и в `C` (для рантайм-значений). В дизайн-доке фиксируем:
оба списка обязаны совпадать; при правке цвета меняем оба.

### 3. Стратегия миграции стилей

- **Статичные стили** (известны на этапе компиляции) → классы Tailwind.
  Нестандартные размеры — arbitrary values: `text-[12.5px]`, `leading-[1.04]`,
  `rounded-[18px]`, `tracking-[-.015em]`, `[font-variant-numeric:tabular-nums]`.
- **Рантайм-стили** (вычисляемая ширина полос `width: barW(v)`, цвет/фон по
  статусу из `statusMeta`, размер плитки `MapView`) → **остаются в `style`**.
  Tailwind не покрывает динамические значения, и это нормальная практика.
- Повторяющиеся «градиентные пятна» hero/unmatched переносятся 1:1 (классы +
  arbitrary, фон-градиенты — `bg-[radial-gradient(...)]` либо `style` если
  громоздко). Приоритет — читабельность, не догма «ноль style».

### 4. Структурный рефактор

Новая раскладка `src/`:

```
src/
├─ App.tsx              # только композиция: hero, controls, main, drawer/modal
├─ index.css            # @import tailwindcss + @theme + неутилитный CSS
├─ theme.ts             # C, statusMeta, barW, fmtInt, fmt1 (FONT_SANS удалён)
├─ types.ts             # без изменений
├─ lib/
│  ├─ report.ts         # без изменений
│  └─ text.ts           # НОВЫЙ: общий clamp(text, max)
└─ components/
   ├─ Header.tsx        # НОВЫЙ: топбар
   ├─ Hero.tsx          # НОВЫЙ: hero + heroStats
   ├─ Controls.tsx      # НОВЫЙ: панель фильтров/сортировок/поиска
   ├─ views/
   │  ├─ GridView.tsx       # из App.tsx
   │  ├─ CompactView.tsx    # из App.tsx
   │  └─ MapView.tsx        # из App.tsx
   ├─ UnmatchedSection.tsx  # из App.tsx
   ├─ Drawer.tsx        # tailwindized
   ├─ AgentModal.tsx    # tailwindized
   └─ shared.tsx        # StatusBadge, LegendItem, metaLine (Bar/pill удалены)
```

Состояние (фильтры/сортировка/drawer) остаётся в `App.tsx` и прокидывается
пропсами — текущая модель данных не меняется, чтобы не раздувать дифф. Вынос
вьюх — чисто механическое перемещение функций в файлы + конвертация классов.

### 5. Границы и интерфейсы

- Каждая вьюха: `({ agents, maxCount?, onOpen })` — тот же контракт, что сейчас.
- `Controls`: контролируемый компонент, получает текущее состояние + сеттеры.
- `clamp` из `lib/text.ts` используют и `App`/`UnmatchedSection`, и `Drawer`.
- `theme.ts` — единственный рантайм-источник цвета; `@theme` — компайл-тайм
  зеркало для классов.

## Обработка ошибок

Чисто презентационный модуль без сетевых вызовов — рантайм-ошибок не
добавляется. Риск миграции — **визуальный регресс**, его и контролируем.

## Тестирование / приёмка

Автотестов в модуле нет и не вводим (вне области). Приёмка:

1. `npm run build` (= `tsc -b && vite build`) проходит без ошибок типов.
2. `npm run dev` — визуальная сверка с текущей версией: hero, 3 вида (Сетка/
   Список/Карта групп), фильтры (статус-чипы, слайдер релевантности, поиск,
   сортировка + направление), drawer, модалка агента, блок «новые идеи».
3. Поведение интеракций без изменений (hover/focus, Escape, блокировка скролла
   под drawer, адаптив).
4. Диф палитры: значения в `@theme` и `C` совпадают.

## Вне области (YAGNI)

- Рефактор слоя данных, `scripts/`, остального репозитория.
- Добавление тёмной темы, новых вью, тестового рантайма, CSS-анимаций сверх
  существующих.
- Изменение модели состояния (Redux/контекст) — пропсов достаточно.
