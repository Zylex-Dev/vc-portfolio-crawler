# Report-Landing Tailwind v4 Migration & Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `report-landing/` from inline `style={{}}` objects to Tailwind CSS v4, split the monolithic `App.tsx` into focused components, and remove dead code — with zero visual change to the rendered page.

**Architecture:** Tailwind v4 via the `@tailwindcss/vite` plugin and a CSS-first `@theme` block that mirrors the existing `theme.ts` palette. Static styles become utility classes (non-standard sizes via arbitrary values for pixel fidelity); runtime-computed styles (bar widths, status colors, tile sizes) stay in `style`. The 460-line `App.tsx` is decomposed into `Header`, `Hero`, `Controls`, three view files, and `UnmatchedSection`; `App` keeps only state + composition.

**Tech Stack:** Vite 5, React 18, TypeScript 5, Tailwind CSS v4.

## Global Constraints

- **Scope:** only `report-landing/`. Do NOT touch `lib/report.ts`, `types.ts`, `src/data/`, `scripts/`, or anything outside this module.
- **Pixel-perfect:** the rendered page must look byte-identical to the current version. Use Tailwind arbitrary values (`text-[12.5px]`, `leading-[1.04]`, `rounded-[18px]`, `tracking-[-.015em]`) for any value not on Tailwind's default scale.
- **No test runtime:** the module has no tests; do not add one. Per-task verification gate is `npm run build` passing + visual check in `npm run dev`.
- **Runtime styles stay inline:** any style whose value is computed at runtime (`barW(v)`, `statusMeta(...)` colors/bg, `MapView` tile `width/height`, drawer open/close transforms) remains in `style={{}}`. Tailwind covers only compile-time-known values.
- **Single palette source of truth:** color values must match between `@theme` in `index.css` and `C` in `theme.ts`. When changing a color, change both.
- **Node:** v20 available. `npm` is the package manager. Run all commands from `report-landing/`.
- **Commit message footer:** end every commit body with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

---

## Conversion Reference (shared by all Tailwind tasks)

This is the concrete recipe every conversion task applies. It is not a placeholder — it is the exact mapping to use.

### Palette → utility class

| `C` key / hex | `@theme` token | Utility examples |
|---|---|---|
| `paper #F4EEE4` | `--color-paper` | `bg-paper` |
| `card #FBF8F2` | `--color-card` | `bg-card` |
| `cardAlt #F7F1E7` | `--color-card-alt` | `bg-card-alt` |
| `border #E7DECF` | `--color-border` | `border-border` |
| `borderWarm #EBE2D2` | `--color-border-warm` | `border-border-warm` |
| `ink #211C16` | `--color-ink` | `text-ink` |
| `inkSoft #5C5345` | `--color-ink-soft` | `text-ink-soft` |
| `muted #837A6C` | `--color-muted` | `text-muted` |
| `faint #A9997F` | `--color-faint` | `text-faint` |
| `track #EDE3D3` | `--color-track` | `bg-track` |
| `clay #C2603C` | `--color-clay` | `text-clay bg-clay` |
| `clayDeep #A6431F` | `--color-clay-deep` | `text-clay-deep` |
| `teal #3F8A78` | `--color-teal` | `text-teal` |
| prod-green `#3F7D55` | `--color-prod` | `text-prod` (runtime use stays inline) |
| dev-amber `#A9781F` | `--color-dev` | `text-dev` |
| prose-brown `#6B5E4D` | `--color-prose` | `text-prose` |
| `FONT_SERIF` | `--font-serif` | `font-serif` |
| `FONT_SANS` | `--font-sans` | `font-sans` (body default) |

One-off hexes that appear only once and only in a runtime/`style` context (e.g. gradient stops `rgba(194,96,60,.20)`, `#EBDCC9`, `#EFE6D6`) do NOT need a token — leave them in `style` or use `bg-[...]`/`border-[...]` arbitrary values inline. Add a token only when the color is reused as a static class.

### Style property → utility (with arbitrary values for off-scale numbers)

| inline style | Tailwind |
|---|---|
| `display:"flex"` | `flex` |
| `alignItems:"center"` | `items-center` |
| `justifyContent:"space-between"` | `justify-between` |
| `gap: 14` | `gap-[14px]` |
| `padding:"15px 28px"` | `px-[28px] py-[15px]` |
| `borderRadius: 18` | `rounded-[18px]` |
| `borderRadius: 99` | `rounded-full` |
| `borderRadius:"50%"` | `rounded-full` |
| `fontSize: 12.5` | `text-[12.5px]` |
| `fontWeight: 700` | `font-bold`; `600`→`font-semibold`; `800`→`font-extrabold`; `500`→`font-medium`; `450/400`→`font-normal` |
| `letterSpacing:"-.015em"` | `tracking-[-.015em]` |
| `lineHeight: 1.04` | `leading-[1.04]` |
| `textTransform:"uppercase"` | `uppercase` |
| `fontVariantNumeric:"tabular-nums"` | `[font-variant-numeric:tabular-nums]` |
| `position:"sticky", top:0` | `sticky top-0` |
| `zIndex: 50` | `z-50` |
| `backdropFilter:"blur(12px)"` | `backdrop-blur-md` (≈12px) — but if exact px matters use `[backdrop-filter:blur(12px)]` |
| `border:`1px solid ${C.border}`` | `border border-border` |
| `cursor:"pointer"` | `cursor-pointer` |
| `whiteSpace:"nowrap"` | `whitespace-nowrap` |
| `overflow:"hidden"` | `overflow-hidden` |
| `maxWidth: 1240` | `max-w-[1240px]` |
| `margin:"0 auto"` | `mx-auto` |
| `-webkit-box` line clamp (3) | `line-clamp-3` |
| `transition:"all .15s"` | `transition-all duration-150` |

### Hover/focus hook classes

The `.agent-card`, `.agent-row`, `.agent-tile`, `.startup-link`, `.agent-title-link` rules in `index.css` move onto the element as utilities when that element is converted, then the now-dead CSS rule is deleted in the same task. Example for `.agent-card`:

```
className="group transition-all duration-150 [box-shadow:0_1px_0_rgba(120,90,50,.03)]
  hover:border-[#D9C3B0] hover:-translate-y-0.5
  hover:[box-shadow:0_10px_26px_-14px_rgba(120,70,40,.28)]
  focus-visible:border-[#D9C3B0] focus-visible:outline-none ..."
```

### What STAYS in `style={{}}`

- `width: barW(a.avgRel)` and any progress-bar fill width.
- `background`/`color`/`borderColor` taken from `statusMeta(...)` (`sm.color`, `sm.bg`).
- `MapView` tile `width: size, height: size` (computed from `Math.sqrt`).
- Drawer overlay `opacity`/`pointerEvents` and panel `transform` driven by the `open` prop.
- Radial-gradient decoration backgrounds (too verbose as classes — keep inline).

---

## File Structure

```
src/
├─ App.tsx               # MODIFY: state + composition only (~120 lines)
├─ index.css             # MODIFY: @import "tailwindcss" + @theme + non-utility CSS
├─ theme.ts              # MODIFY: remove FONT_SANS; keep C, statusMeta, barW, fmtInt, fmt1
├─ types.ts              # unchanged
├─ lib/
│  ├─ report.ts          # unchanged
│  └─ text.ts            # CREATE: shared clamp(text, max)
└─ components/
   ├─ Header.tsx         # CREATE (from App.tsx)
   ├─ Hero.tsx           # CREATE (from App.tsx)
   ├─ Controls.tsx       # CREATE (from App.tsx)
   ├─ UnmatchedSection.tsx # CREATE (from App.tsx)
   ├─ shared.tsx         # MODIFY: StatusBadge + metaLine + LegendItem; drop Bar, pill
   ├─ Drawer.tsx         # MODIFY: tailwindize, use lib/text clamp
   ├─ AgentModal.tsx     # MODIFY: tailwindize
   └─ views/
      ├─ GridView.tsx    # CREATE (from App.tsx)
      ├─ CompactView.tsx # CREATE (from App.tsx)
      └─ MapView.tsx     # CREATE (from App.tsx)
```

---

### Task 1: Install Tailwind v4 and wire the build

**Files:**
- Modify: `report-landing/package.json` (devDependencies — via npm)
- Modify: `report-landing/vite.config.ts`
- Modify: `report-landing/src/index.css`

**Interfaces:**
- Consumes: nothing.
- Produces: working Tailwind utility classes + `@theme` tokens (`bg-paper`, `text-ink`, `font-serif`, etc.) available to all later tasks. The existing inline styles remain intact and continue to render — Tailwind is added alongside them.

- [ ] **Step 1: Install Tailwind v4 + Vite plugin**

```bash
cd report-landing
npm i -D tailwindcss@^4 @tailwindcss/vite@^4
```

- [ ] **Step 2: Add the plugin to Vite**

Edit `vite.config.ts` to:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Relative base so the static bundle works from any GitHub Pages subpath
// (https://user.github.io/<repo>/) without hardcoding the repo name.
export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss()],
  build: {
    outDir: "dist",
    assetsInlineLimit: 0,
  },
});
```

- [ ] **Step 3: Rewrite `index.css` — Tailwind import, `@theme` tokens, keep non-utility CSS**

Replace the whole file with:

```css
@import "tailwindcss";

@theme {
  --color-paper: #F4EEE4;
  --color-card: #FBF8F2;
  --color-card-alt: #F7F1E7;
  --color-border: #E7DECF;
  --color-border-warm: #EBE2D2;
  --color-ink: #211C16;
  --color-ink-soft: #5C5345;
  --color-muted: #837A6C;
  --color-faint: #A9997F;
  --color-track: #EDE3D3;
  --color-clay: #C2603C;
  --color-clay-deep: #A6431F;
  --color-teal: #3F8A78;
  --color-prod: #3F7D55;
  --color-dev: #A9781F;
  --color-prose: #6B5E4D;

  --font-sans: "Hanken Grotesk", system-ui, sans-serif;
  --font-serif: "Newsreader", serif;

  --animate-fade-up: fadeUp 0.5s both;
  --animate-fade-in: fadeIn 0.2s both;
}

html,
body {
  margin: 0;
  padding: 0;
}
body {
  background: #F4EEE4;
  font-family: var(--font-sans);
  color: #211C16;
  -webkit-font-smoothing: antialiased;
}
::selection {
  background: #EAD3C2;
}

/* range slider — clay thumb on sand track */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 99px;
  background: #E0D5C2;
  outline: none;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #C2603C;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(60, 40, 20, 0.25);
}
input[type="range"]::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #C2603C;
  cursor: pointer;
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
::-webkit-scrollbar-thumb {
  background: #D8CCB8;
  border-radius: 99px;
  border: 2px solid #F4EEE4;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* hover/focus hook classes — removed per-component as elements are tailwindized */
.agent-card { transition: all 0.16s; box-shadow: 0 1px 0 rgba(120, 90, 50, 0.03); }
.agent-card:hover,
.agent-card:focus-visible { border-color: #D9C3B0; box-shadow: 0 10px 26px -14px rgba(120, 70, 40, 0.28); transform: translateY(-2px); outline: none; }
.agent-row { transition: background 0.14s; }
.agent-row:hover,
.agent-row:focus-visible { background: #F5EEE0; outline: none; }
.agent-tile { transition: transform 0.14s; }
.agent-tile:hover,
.agent-tile:focus-visible { transform: scale(1.04); outline: none; }
.startup-link { transition: color 0.14s; }
.startup-link:hover,
.startup-link:focus-visible { color: #C2603C !important; text-decoration: underline; text-underline-offset: 3px; outline: none; }
.agent-title-link { cursor: pointer; background: none; border: none; padding: 0; text-align: left; transition: color 0.14s; }
.agent-title-link:hover,
.agent-title-link:focus-visible { color: #C2603C !important; text-decoration: underline; text-underline-offset: 4px; text-decoration-thickness: 1.5px; outline: none; }
:focus-visible { outline: 2px solid #C2603C; outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}
```

Note: `select`/`button` `font-family: inherit` is dropped because `--font-sans` is now the inherited body font; Tailwind's preflight already sets `font: inherit` on form controls.

- [ ] **Step 4: Verify build passes**

Run: `npm run build`
Expected: `tsc -b` and `vite build` both succeed, `dist/` produced. Tailwind's preflight is now active.

- [ ] **Step 5: Verify the page still renders**

Run: `npm run dev`, open http://localhost:5173
Expected: page renders. Preflight may have minor margin resets, but inline styles dominate so layout is essentially unchanged. Confirm hero, controls, cards, drawer all appear.

- [ ] **Step 6: Commit**

```bash
git add report-landing/package.json report-landing/package-lock.json report-landing/vite.config.ts report-landing/src/index.css
git commit -m "build(report): add Tailwind v4 via @tailwindcss/vite + @theme tokens

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Add shared `clamp` util and remove dead code

**Files:**
- Create: `report-landing/src/lib/text.ts`
- Modify: `report-landing/src/theme.ts` (remove `FONT_SANS`)
- Modify: `report-landing/src/components/shared.tsx` (remove `Bar`, `pill`, unused imports)

**Interfaces:**
- Consumes: nothing.
- Produces: `clamp(text: string, max: number): string` exported from `lib/text.ts`. Used by `App`/`UnmatchedSection`/`Drawer` in later tasks. `FONT_SERIF` stays in `theme.ts`; `FONT_SANS` is removed.

- [ ] **Step 1: Create `src/lib/text.ts`**

```ts
/** Truncate to `max` chars, trimming trailing space and appending an ellipsis. */
export function clamp(text: string, max: number): string {
  if (!text) return "";
  return text.length <= max ? text : text.slice(0, max).trimEnd() + "…";
}
```

- [ ] **Step 2: Remove `FONT_SANS` from `theme.ts`**

Delete this line from `src/theme.ts`:

```ts
export const FONT_SANS = "'Hanken Grotesk',system-ui,sans-serif";
```

Keep `export const FONT_SERIF = "'Newsreader',serif";`.

- [ ] **Step 3: Remove dead `Bar` and `pill` from `shared.tsx`**

In `src/components/shared.tsx`, delete the entire `Bar` function (the `export function Bar({ ... }) { ... }` block) and the `pill` const (`export const pill: CSSProperties = { ... };`). Then remove now-unused imports: drop `CSSProperties` from the React type import, and drop `barW` from the `../theme` import (keep `C`). After this, `shared.tsx` exports only `metaLine` and `StatusBadge`.

- [ ] **Step 4: Verify build passes (catches any lingering references)**

Run: `npm run build`
Expected: success. If `tsc` reports an unused/missing import, fix it. (Confirmed via grep that `Bar`, `pill`, `FONT_SANS` have no consumers.)

- [ ] **Step 5: Commit**

```bash
git add report-landing/src/lib/text.ts report-landing/src/theme.ts report-landing/src/components/shared.tsx
git commit -m "refactor(report): extract shared clamp util, drop dead Bar/pill/FONT_SANS

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Tailwindize `shared.tsx` and add `LegendItem`

**Files:**
- Modify: `report-landing/src/components/shared.tsx`

**Interfaces:**
- Consumes: `@theme` tokens (Task 1), Conversion Reference.
- Produces: `StatusBadge({ label, color, bg, small })`, `metaLine(s)`, and `LegendItem({ color, text, square? })` — all from `components/shared.tsx`. `LegendItem` is moved here from `App.tsx` so views/App can import it.

- [ ] **Step 1: Convert `StatusBadge` to Tailwind (color/bg stay inline — runtime)**

Replace the `StatusBadge` body's outer `<span style={{...}}>` with className utilities, keeping `background`/`color` inline because they are runtime props:

```tsx
export function StatusBadge({ label, color, bg, small }: { label: string; color: string; bg: string; small?: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-[6px] font-bold rounded-full whitespace-nowrap ${
        small ? "text-[11.5px] px-[9px] py-[4px]" : "text-[12px] px-[10px] py-[4px]"
      }`}
      style={{ background: bg, color }}
    >
      <span className="w-[6px] h-[6px] rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}
```

- [ ] **Step 2: Add `LegendItem` (moved from `App.tsx`)**

Append to `shared.tsx`:

```tsx
export function LegendItem({ color, text, square }: { color: string; text: string; square?: boolean }) {
  return (
    <span className="inline-flex items-center gap-[6px]">
      <span className={`w-[9px] h-[9px] ${square ? "rounded-[2px]" : "rounded-full"}`} style={{ background: color }} />
      {text}
    </span>
  );
}
```

- [ ] **Step 3: Verify build passes**

Run: `npm run build`
Expected: success (App.tsx still has its own local `LegendItem` for now — duplicate name is fine because it's a separate module scope; it gets removed in Task 11).

- [ ] **Step 4: Commit**

```bash
git add report-landing/src/components/shared.tsx
git commit -m "refactor(report): tailwindize StatusBadge, add shared LegendItem

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Extract & tailwindize `Header.tsx`

**Files:**
- Create: `report-landing/src/components/Header.tsx`
- Modify: `report-landing/src/App.tsx` (replace inline `<header>` with `<Header />`)

**Interfaces:**
- Consumes: Conversion Reference.
- Produces: `default export function Header()` — no props (static topbar).

- [ ] **Step 1: Create `Header.tsx`** (convert the current `<header>` block from `App.tsx` lines ~150-166)

```tsx
export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-[rgba(244,238,228,.86)] [backdrop-filter:blur(12px)]">
      <div className="mx-auto flex max-w-[1240px] items-center justify-center gap-[13px] px-[28px] py-[15px]">
        <div className="flex h-[34px] w-[34px] items-center justify-center rounded-[10px] bg-clay text-[18px] font-extrabold text-white">
          П
        </div>
        <div className="text-[21px] font-bold tracking-[-.015em]">ПМО - Карта рынка агентов</div>
      </div>
    </header>
  );
}
```

- [ ] **Step 2: Wire into `App.tsx`**

Add `import Header from "./components/Header";` and replace the entire inline `<header>…</header>` block with `<Header />`.

- [ ] **Step 3: Verify build + visual**

Run: `npm run build` then `npm run dev`. Expected: success; topbar looks identical (centered logo chip «П» + title, sticky, blurred).

- [ ] **Step 4: Commit**

```bash
git add report-landing/src/components/Header.tsx report-landing/src/App.tsx
git commit -m "refactor(report): extract Header component (tailwind)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Extract & tailwindize `Hero.tsx`

**Files:**
- Create: `report-landing/src/components/Hero.tsx`
- Modify: `report-landing/src/App.tsx`

**Interfaces:**
- Consumes: `ReportMeta` from `../types`, `fmtInt` + `FONT_SERIF` from `../theme`, Conversion Reference.
- Produces: `default export function Hero({ meta }: { meta: ReportMeta })`. The `heroStats` array (currently in `App.tsx` lines ~138-145) moves into `Hero`.

- [ ] **Step 1: Create `Hero.tsx`**

Move the `heroStats` definition and the entire `<section>` hero block (App.tsx ~168-196) here. Decorative radial-gradient layers and the dotted background stay as inline `style` (runtime-verbose). Static text/layout becomes utilities. Stat-value `color` stays inline (per-stat runtime value `s.color`).

```tsx
import type { ReportMeta } from "../types";
import { C, FONT_SERIF, fmtInt } from "../theme";

export default function Hero({ meta }: { meta: ReportMeta }) {
  const heroStats = [
    { v: fmtInt(meta.totalCollected), l: "стартапов собрано", color: C.ink },
    { v: fmtInt(meta.totalStartups), l: "EdTech отфильтровано", color: C.ink },
    { v: fmtInt(meta.totalAgents), l: "ИИ-агентов ПМО", color: C.ink },
    { v: fmtInt(meta.matched), l: "сматчено с агентами", color: C.teal },
    { v: fmtInt(meta.unmatched), l: "новых идей вне покрытия", color: C.clay },
    { v: fmtInt(meta.totalFunds), l: "венчурных фондов", color: C.ink },
  ];

  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="absolute inset-0 opacity-50" style={{ backgroundImage: "radial-gradient(#D9CDB6 1.1px,transparent 1.1px)", backgroundSize: "24px 24px" }} />
      <div className="absolute -top-[160px] -right-[120px] h-[520px] w-[520px] rounded-full" style={{ background: "radial-gradient(circle,rgba(194,96,60,.20),transparent 65%)" }} />
      <div className="absolute -bottom-[200px] -left-[100px] h-[480px] w-[480px] rounded-full" style={{ background: "radial-gradient(circle,rgba(63,138,120,.14),transparent 65%)" }} />
      <div className="relative mx-auto max-w-[1240px] px-[28px] pb-[40px] pt-[64px] [animation:fadeUp_.5s_both]">
        <div className="mb-[24px] inline-flex items-center gap-[8px] rounded-full border border-border bg-white px-[14px] py-[6px] text-[12.5px] font-semibold text-[#9A6A4A]">
          <span className="h-[7px] w-[7px] rounded-full bg-clay" />
          Исследование венчурных портфелей 2026
        </div>
        <h1 className="m-0 mb-[18px] text-[54px] font-normal leading-[1.04] tracking-[-.015em]" style={{ fontFamily: FONT_SERIF }}>
          Лучшие мировые практики EdTech&nbsp;стартапов для воплощения ПМО на практике
        </h1>
        <p className="m-0 mb-[40px] max-w-[62ch] text-[18px] font-normal leading-[1.55] text-ink-soft">
          Мы собрали <b className="font-bold text-ink">{fmtInt(meta.totalCollected)}</b> стартапов из портфелей крупных венчурных фондов,
          отфильтровали <b className="font-bold text-ink">{fmtInt(meta.totalStartups)}</b> EdTech-решений и сопоставили каждое
          с <b className="font-bold text-ink">{meta.totalAgents}</b> ИИ-агентами персонализированной модели образования.
          Ниже — интерактивная карта совпадений и зона новых идей.
        </p>
        <div className="grid gap-px overflow-hidden rounded-[18px] border border-border bg-border" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))" }}>
          {heroStats.map((s) => (
            <div key={s.l} className="bg-card px-[22px] pb-[20px] pt-[22px]">
              <div className="text-[34px] leading-none tracking-[-.02em] [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF, color: s.color }}>{s.v}</div>
              <div className="mt-[8px] text-[12.5px] font-medium leading-[1.35] text-[#837A6C]">{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Wire into `App.tsx`**

Add `import Hero from "./components/Hero";`, remove the local `heroStats` array, and replace the hero `<section>` with `<Hero meta={meta} />`.

- [ ] **Step 3: Verify build + visual**

Run: `npm run build` then `npm run dev`. Expected: hero identical — badge, serif headline, paragraph with bold numbers, 6-cell stat grid with hairline separators and correct value colors (ink/teal/clay).

- [ ] **Step 4: Commit**

```bash
git add report-landing/src/components/Hero.tsx report-landing/src/App.tsx
git commit -m "refactor(report): extract Hero component (tailwind)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Extract & tailwindize `Controls.tsx`

**Files:**
- Create: `report-landing/src/components/Controls.tsx`
- Modify: `report-landing/src/App.tsx`

**Interfaces:**
- Consumes: Conversion Reference. `View`, `SortKey` types and the `VIEW_MODES`/`STATUS_CHIPS` constants (currently in `App.tsx` lines ~12-25) move into `Controls`. Export the types so `App` can keep its state typed.
- Produces:
```ts
export type View = "grid" | "compact" | "map";
export type SortKey = "count" | "relevance" | "pmo" | "name" | "status";
export default function Controls(props: {
  view: View; setView: (v: View) => void;
  status: string; setStatus: (v: string) => void;
  minRel: number; setMinRel: (v: number) => void;
  q: string; setQ: (v: string) => void;
  sort: SortKey; setSort: (v: SortKey) => void;
  dir: "asc" | "desc"; setDir: (v: "asc" | "desc") => void;
}): JSX.Element
```

- [ ] **Step 1: Create `Controls.tsx`**

Move `View`, `SortKey`, `VIEW_MODES`, `STATUS_CHIPS` here (export `View`/`SortKey`). Convert the sticky controls `<div>` (App.tsx ~198-261). The active-state colors that flip on `on` (e.g. `background: on ? C.ink : "transparent"`) stay inline since they are conditional/runtime; layout/shape become utilities. The chip dot `background` stays inline.

```tsx
import { C } from "../theme";

export type View = "grid" | "compact" | "map";
export type SortKey = "count" | "relevance" | "pmo" | "name" | "status";

const VIEW_MODES: { v: View; label: string }[] = [
  { v: "grid", label: "Сетка" },
  { v: "compact", label: "Список" },
  { v: "map", label: "Карта групп" },
];

const STATUS_CHIPS: { v: string; label: string; dot: string }[] = [
  { v: "all", label: "Все", dot: "transparent" },
  { v: "Протестировать", label: "В проде", dot: "#3F7D55" },
  { v: "В разработке", label: "В разработке", dot: "#A9781F" },
];

export default function Controls({
  view, setView, status, setStatus, minRel, setMinRel, q, setQ, sort, setSort, dir, setDir,
}: {
  view: View; setView: (v: View) => void;
  status: string; setStatus: (v: string) => void;
  minRel: number; setMinRel: (v: number) => void;
  q: string; setQ: (v: string) => void;
  sort: SortKey; setSort: (v: SortKey) => void;
  dir: "asc" | "desc"; setDir: (v: "asc" | "desc") => void;
}) {
  return (
    <div className="sticky top-[53px] z-40 border-b border-border bg-[rgba(244,238,228,.92)] [backdrop-filter:blur(12px)]">
      <div className="mx-auto flex max-w-[1240px] flex-wrap items-center gap-[14px] px-[28px] py-[14px]">
        {/* view toggle */}
        <div className="flex gap-[4px] rounded-full border border-[#E1D6C2] bg-[#EBE2D2] p-[4px]">
          {VIEW_MODES.map((m) => {
            const on = view === m.v;
            return (
              <button
                key={m.v}
                onClick={() => setView(m.v)}
                className="cursor-pointer rounded-full px-[15px] py-[7px] text-[13px] font-semibold transition-all duration-150"
                style={{ background: on ? C.ink : "transparent", color: on ? "#fff" : C.muted }}
              >
                {m.label}
              </button>
            );
          })}
        </div>

        {/* status chips */}
        <div className="flex flex-wrap items-center gap-[8px]">
          {STATUS_CHIPS.map((c) => {
            const on = status === c.v;
            return (
              <button
                key={c.v}
                onClick={() => setStatus(c.v)}
                className="inline-flex cursor-pointer items-center gap-[7px] rounded-full border px-[13px] py-[7px] text-[12.5px] font-semibold transition-all duration-150"
                style={{ borderColor: on ? C.ink : C.border, background: on ? C.ink : "#fff", color: on ? "#fff" : "#4A4339" }}
              >
                <span className="h-[7px] w-[7px] rounded-full" style={{ background: on ? (c.v === "all" ? "#fff" : c.dot) : c.dot }} />
                {c.label}
              </button>
            );
          })}
        </div>

        {/* relevance slider */}
        <div className="flex items-center gap-[11px] rounded-full border border-border bg-white px-[15px] py-[7px]">
          <span className="whitespace-nowrap text-[12.5px] font-semibold text-muted">Релевантность ≥</span>
          <input type="range" min={0} max={10} step={1} value={minRel} onChange={(e) => setMinRel(Number(e.target.value))} className="w-[108px]" aria-label="Минимальная релевантность" />
          <span className="min-w-[34px] text-[12.5px] font-bold text-clay [font-variant-numeric:tabular-nums]">{minRel === 0 ? "любая" : minRel}</span>
        </div>

        <div className="flex-1" />

        {/* search */}
        <div className="relative flex items-center rounded-full border border-border bg-white pl-[14px] pr-[6px]">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#A9997F" strokeWidth="2.2">
            <circle cx="11" cy="11" r="7" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input type="text" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Поиск агента…" aria-label="Поиск агента" className="w-[140px] border-none bg-transparent px-[8px] py-[8px] text-[13px] text-ink outline-none" />
        </div>

        {/* sort */}
        <div className="flex items-center gap-[6px]">
          <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)} aria-label="Сортировка" className="cursor-pointer rounded-full border border-border bg-white px-[13px] py-[8px] text-[12.5px] font-semibold text-[#4A4339] outline-none">
            <option value="count">По размеру группы</option>
            <option value="relevance">По релевантности</option>
            <option value="pmo">По соответствию ПМО 2.0</option>
            <option value="name">По названию</option>
            <option value="status">По статусу</option>
          </select>
          <button onClick={() => setDir(dir === "asc" ? "desc" : "asc")} title="Направление" aria-label="Направление сортировки" className="flex h-[34px] w-[34px] cursor-pointer items-center justify-center rounded-full border border-border bg-white text-[14px] text-[#4A4339]">
            {dir === "asc" ? "↑" : "↓"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Wire into `App.tsx`**

Add `import Controls, { type View, type SortKey } from "./components/Controls";`. Remove the local `View`/`SortKey` type aliases and `VIEW_MODES`/`STATUS_CHIPS` consts. Replace the controls `<div>` with:

```tsx
<Controls view={view} setView={setView} status={status} setStatus={setStatus} minRel={minRel} setMinRel={setMinRel} q={q} setQ={setQ} sort={sort} setSort={setSort} dir={dir} setDir={setDir} />
```

- [ ] **Step 3: Verify build + visual**

Run: `npm run build` then `npm run dev`. Expected: controls identical and interactive — view toggle, status chips (active = ink fill), slider with «любая»/number readout, search with magnifier icon, sort select + direction button. Filtering/sorting still works.

- [ ] **Step 4: Commit**

```bash
git add report-landing/src/components/Controls.tsx report-landing/src/App.tsx
git commit -m "refactor(report): extract Controls component (tailwind)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 7: Extract & tailwindize `views/GridView.tsx`

**Files:**
- Create: `report-landing/src/components/views/GridView.tsx`
- Modify: `report-landing/src/App.tsx`
- Modify: `report-landing/src/index.css` (delete `.agent-card` rules)

**Interfaces:**
- Consumes: `AgentGroup` from `../../types`, `statusMeta`/`FONT_SERIF`/`fmtInt`/`C` from `../../theme`, `StatusBadge` from `../shared`.
- Produces: `default export function GridView({ agents, onOpen }: { agents: AgentGroup[]; onOpen: (id: number) => void })`.

- [ ] **Step 1: Create `views/GridView.tsx`**

Move `GridView` from `App.tsx` (~308-333). Convert; the `.agent-card` hook becomes inline hover/focus utilities. Card border uses `border-border-warm`; the top-divider `#EFE6D6` stays as an arbitrary value. `minHeight:"3.75em"` and line-clamp:

```tsx
import type { AgentGroup } from "../../types";
import { C, FONT_SERIF, fmtInt, statusMeta } from "../../theme";
import { StatusBadge } from "../shared";

export default function GridView({ agents, onOpen }: { agents: AgentGroup[]; onOpen: (id: number) => void }) {
  return (
    <div className="grid gap-[14px]" style={{ gridTemplateColumns: "repeat(auto-fill,minmax(286px,1fr))" }}>
      {agents.map((a) => {
        const sm = statusMeta(a.status);
        return (
          <button
            key={a.id}
            onClick={() => onOpen(a.id)}
            className="flex cursor-pointer flex-col gap-[14px] rounded-[18px] border border-border-warm bg-card px-[18px] pb-[16px] pt-[18px] text-left transition-all duration-150 [box-shadow:0_1px_0_rgba(120,90,50,.03)] hover:-translate-y-0.5 hover:border-[#D9C3B0] hover:[box-shadow:0_10px_26px_-14px_rgba(120,70,40,.28)] focus-visible:border-[#D9C3B0] focus-visible:outline-none"
          >
            <div className="flex items-center justify-between gap-[8px]">
              <span className="text-[11px] font-bold uppercase tracking-[.02em] text-faint">{a.category}</span>
              <StatusBadge label={sm.label} color={sm.color} bg={sm.bg} small />
            </div>
            <div className="line-clamp-3 min-h-[3.75em] text-[19px] font-bold leading-[1.25] tracking-[-.01em] text-ink" title={a.name}>{a.name}</div>
            <div className="mt-auto flex items-baseline justify-between gap-[8px] border-t border-[#EFE6D6] pt-[11px]">
              <span className="flex items-baseline gap-[7px]">
                <span className="text-[32px] leading-none tracking-[-.02em] text-ink [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF }}>{fmtInt(a.count)}</span>
                <span className="text-[12.5px] font-medium text-muted">стартапов</span>
              </span>
              <span className="text-[12.5px] font-bold text-clay">Открыть →</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
```
(Keep the `C` import only if used; if not referenced after conversion, omit it to satisfy `tsc noUnusedLocals` if enabled.)

- [ ] **Step 2: Wire into `App.tsx`**

Add `import GridView from "./components/views/GridView";` and remove the local `GridView` function.

- [ ] **Step 3: Delete now-dead `.agent-card` CSS**

In `src/index.css`, delete the `.agent-card { ... }` and `.agent-card:hover, .agent-card:focus-visible { ... }` rules.

- [ ] **Step 4: Verify build + visual**

Run: `npm run build` then `npm run dev`, default «Сетка» view. Expected: cards identical — category eyebrow, status badge, 3-line clamped name, big serif count + «стартапов», «Открыть →»; hover lifts the card with shadow.

- [ ] **Step 5: Commit**

```bash
git add report-landing/src/components/views/GridView.tsx report-landing/src/App.tsx report-landing/src/index.css
git commit -m "refactor(report): extract GridView (tailwind), drop .agent-card css

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 8: Extract & tailwindize `views/CompactView.tsx`

**Files:**
- Create: `report-landing/src/components/views/CompactView.tsx`
- Modify: `report-landing/src/App.tsx`
- Modify: `report-landing/src/index.css` (delete `.agent-row` rules)

**Interfaces:**
- Consumes: `AgentGroup` from `../../types`, `C`/`barW`/`fmt1`/`fmtInt`/`statusMeta` from `../../theme`.
- Produces: `default export function CompactView({ agents, maxCount, onOpen }: { agents: AgentGroup[]; maxCount: number; onOpen: (id: number) => void })`.

- [ ] **Step 1: Create `views/CompactView.tsx`**

Move `CompactView` from `App.tsx` (~336-382). The shared `cols` grid-template stays inline (`style={{ gridTemplateColumns: cols }}`). Bar fill widths (`barW(...)`, `(a.count/maxCount)*100%`) and the status dot color stay inline. `.agent-row` hook → `hover:bg-[#F5EEE0] focus-visible:bg-[#F5EEE0] focus-visible:outline-none`.

```tsx
import type { AgentGroup } from "../../types";
import { C, barW, fmt1, fmtInt, statusMeta } from "../../theme";

export default function CompactView({ agents, maxCount, onOpen }: { agents: AgentGroup[]; maxCount: number; onOpen: (id: number) => void }) {
  const cols = "1fr 120px 116px 116px 40px";
  return (
    <div className="overflow-hidden rounded-[18px] border border-border-warm bg-card">
      <div className="grid gap-[14px] border-b border-[#EFE6D6] px-[20px] py-[13px] text-[11px] font-bold uppercase tracking-[.03em] text-faint" style={{ gridTemplateColumns: cols }}>
        <span>Агент</span>
        <span>Группа</span>
        <span>Релевантность</span>
        <span>Соответствие ПМО 2.0</span>
        <span />
      </div>
      {agents.map((a) => {
        const sm = statusMeta(a.status);
        return (
          <button
            key={a.id}
            onClick={() => onOpen(a.id)}
            className="grid w-full cursor-pointer items-center gap-[14px] border-b border-[#F0E8D9] bg-transparent px-[20px] py-[13px] text-left transition-[background] duration-150 hover:bg-[#F5EEE0] focus-visible:bg-[#F5EEE0] focus-visible:outline-none"
            style={{ gridTemplateColumns: cols }}
          >
            <span className="flex min-w-0 items-center gap-[11px]">
              <span className="h-[8px] w-[8px] flex-none rounded-full" style={{ background: sm.color }} />
              <span className="min-w-0">
                <span className="block overflow-hidden text-ellipsis whitespace-nowrap text-[14.5px] font-bold tracking-[-.01em]">{a.name}</span>
                <span className="block text-[11.5px] font-medium text-faint">{a.category}</span>
              </span>
            </span>
            <span className="flex items-center gap-[9px]">
              <span className="min-w-[30px] text-[15px] font-bold [font-variant-numeric:tabular-nums]">{fmtInt(a.count)}</span>
              <span className="h-[6px] flex-1 overflow-hidden rounded-full bg-track">
                <span className="block h-full bg-[#C9A98C]" style={{ width: `${Math.round((a.count / maxCount) * 100)}%` }} />
              </span>
            </span>
            <span className="flex items-center gap-[8px]">
              <span className="h-[6px] flex-1 overflow-hidden rounded-full bg-track">
                <span className="block h-full bg-clay" style={{ width: barW(a.avgRel) }} />
              </span>
              <span className="text-[12.5px] font-bold text-clay [font-variant-numeric:tabular-nums]">{fmt1(a.avgRel)}</span>
            </span>
            <span className="flex items-center gap-[8px]">
              <span className="h-[6px] flex-1 overflow-hidden rounded-full bg-track">
                <span className="block h-full bg-teal" style={{ width: barW(a.avgPmo) }} />
              </span>
              <span className="text-[12.5px] font-bold text-teal [font-variant-numeric:tabular-nums]">{fmt1(a.avgPmo)}</span>
            </span>
            <span className="text-right text-[15px] font-bold text-clay">→</span>
          </button>
        );
      })}
    </div>
  );
}
```
(Drop the `C` import if unused after conversion.)

- [ ] **Step 2: Wire into `App.tsx`**

Add `import CompactView from "./components/views/CompactView";` and remove the local `CompactView` function.

- [ ] **Step 3: Delete `.agent-row` CSS** from `src/index.css`.

- [ ] **Step 4: Verify build + visual**

Run: `npm run build` then `npm run dev`, switch to «Список». Expected: table identical — header row, status dot, name+category, count bar (`#C9A98C`), clay relevance bar, teal ПМО bar, «→»; rows highlight on hover.

- [ ] **Step 5: Commit**

```bash
git add report-landing/src/components/views/CompactView.tsx report-landing/src/App.tsx report-landing/src/index.css
git commit -m "refactor(report): extract CompactView (tailwind), drop .agent-row css

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 9: Extract & tailwindize `views/MapView.tsx`

**Files:**
- Create: `report-landing/src/components/views/MapView.tsx`
- Modify: `report-landing/src/App.tsx`
- Modify: `report-landing/src/index.css` (delete `.agent-tile` rules)

**Interfaces:**
- Consumes: `AgentGroup` from `../../types`, `FONT_SERIF`/`fmtInt`/`statusMeta` from `../../theme`.
- Produces: `default export function MapView({ agents, maxCount, onOpen }: { agents: AgentGroup[]; maxCount: number; onOpen: (id: number) => void })`.

- [ ] **Step 1: Create `views/MapView.tsx`**

Move `MapView` from `App.tsx` (~385-403). Tile `width/height` (computed `size`) and `border/background/color` (from `sm`) stay inline. `.agent-tile` hook → `transition-transform duration-150 hover:scale-[1.04] focus-visible:scale-[1.04] focus-visible:outline-none`.

```tsx
import type { AgentGroup } from "../../types";
import { FONT_SERIF, fmtInt, statusMeta } from "../../theme";

export default function MapView({ agents, maxCount, onOpen }: { agents: AgentGroup[]; maxCount: number; onOpen: (id: number) => void }) {
  return (
    <div className="rounded-[18px] border border-border-warm bg-card p-[22px]">
      <p className="m-0 mb-[18px] text-[13px] font-medium text-muted">Размер плитки — число стартапов в группе. Цвет — стадия реализации агента.</p>
      <div className="flex flex-wrap items-end gap-[10px]">
        {agents.map((a) => {
          const sm = statusMeta(a.status);
          const size = Math.round(54 + Math.sqrt(a.count / maxCount) * 116);
          return (
            <button
              key={a.id}
              onClick={() => onOpen(a.id)}
              title={a.name}
              className="flex cursor-pointer flex-col justify-between overflow-hidden rounded-[13px] border p-[10px] transition-transform duration-150 hover:scale-[1.04] focus-visible:scale-[1.04] focus-visible:outline-none"
              style={{ borderColor: sm.color, background: sm.bg, color: sm.color, width: size, height: size }}
            >
              <span className="line-clamp-2 overflow-hidden text-[11px] font-bold leading-[1.15]">{a.name}</span>
              <span className="self-end text-[21px] leading-none [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF }}>{fmtInt(a.count)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Wire into `App.tsx`**

Add `import MapView from "./components/views/MapView";` and remove the local `MapView` function.

- [ ] **Step 3: Delete `.agent-tile` CSS** from `src/index.css`.

- [ ] **Step 4: Verify build + visual**

Run: `npm run build` then `npm run dev`, switch to «Карта групп». Expected: tiles identical — sized by sqrt(count), colored by status, 2-line name + serif count; hover scales the tile.

- [ ] **Step 5: Commit**

```bash
git add report-landing/src/components/views/MapView.tsx report-landing/src/App.tsx report-landing/src/index.css
git commit -m "refactor(report): extract MapView (tailwind), drop .agent-tile css

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 10: Extract & tailwindize `UnmatchedSection.tsx`

**Files:**
- Create: `report-landing/src/components/UnmatchedSection.tsx`
- Modify: `report-landing/src/App.tsx`

**Interfaces:**
- Consumes: `UnmatchedBucket` from `../lib/report`, `Startup` from `../types`, `C`/`FONT_SERIF`/`fmt1`/`fmtInt` from `../theme`, `metaLine` from `./shared`, `clamp` from `../lib/text`.
- Produces: `default export function UnmatchedSection({ unmatched, onOpen }: { unmatched: UnmatchedBucket; onOpen: () => void })`. Note: type the prop as `UnmatchedBucket` (exported from `lib/report.ts`) instead of the current `ReturnType<typeof enrich>["unmatched"]`.

- [ ] **Step 1: Create `UnmatchedSection.tsx`**

Move `UnmatchedSection` from `App.tsx` (~406-453) and use the shared `clamp` instead of the local `clampText`. Decorative radial gradient + the section background gradient stay inline. The clay CTA button keeps its inline `boxShadow`/`background`.

```tsx
import type { Startup } from "../types";
import type { UnmatchedBucket } from "../lib/report";
import { C, FONT_SERIF, fmt1, fmtInt } from "../theme";
import { metaLine } from "./shared";
import { clamp } from "../lib/text";

export default function UnmatchedSection({ unmatched, onOpen }: { unmatched: UnmatchedBucket; onOpen: () => void }) {
  const samples: Startup[] = [...unmatched.group].sort((a, b) => b.pmoScore - a.pmoScore).slice(0, 4);
  return (
    <section className="relative mt-[46px] overflow-hidden rounded-[24px] border border-[#E6CDB8]" style={{ background: "linear-gradient(135deg,#FBEDE2,#F7F0E4)" }}>
      <div className="absolute -top-[90px] -right-[60px] h-[340px] w-[340px] rounded-full" style={{ background: "radial-gradient(circle,rgba(194,96,60,.16),transparent 65%)" }} />
      <div className="relative px-[32px] py-[34px]">
        <div className="mb-[26px] flex flex-wrap items-end justify-between gap-[20px]">
          <div className="max-w-[54ch]">
            <div className="mb-[16px] inline-flex items-center gap-[8px] rounded-full border border-[#E6CDB8] bg-white px-[13px] py-[5px] text-[12px] font-bold text-clay-deep">
              <span className="h-[7px] w-[7px] rounded-full bg-clay" />
              Зона новых идей
            </div>
            <h2 className="m-0 mb-[10px] text-[30px] font-normal leading-[1.1] tracking-[-.015em]" style={{ fontFamily: FONT_SERIF }}>
              {fmtInt(unmatched.count)} стартапов вне покрытия 44 агентов
            </h2>
            <p className="m-0 text-[15px] font-normal leading-[1.55] text-prose">
              Эти команды не совпали ни с одним нашим агентом — самый ценный срез исследования. Каждый из них — кандидат на новую продуктовую гипотезу для пайплайна ПМО.
            </p>
          </div>
          <button onClick={onOpen} className="cursor-pointer whitespace-nowrap rounded-full border-none bg-clay px-[22px] py-[13px] text-[14px] font-bold text-white" style={{ boxShadow: "0 8px 20px -8px rgba(194,96,60,.6)" }}>
            Смотреть все {fmtInt(unmatched.count)} →
          </button>
        </div>
        <div className="mb-[22px] flex flex-wrap gap-[10px]">
          <div className="rounded-[13px] border border-[#EBDCC9] bg-white px-[18px] py-[13px]">
            <div className="text-[25px] leading-none text-teal [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF }}>{fmt1(unmatched.avgPmo)}</div>
            <div className="mt-[5px] text-[11.5px] font-semibold text-[#9A8F7C]">среднее соответствие ПМО 2.0</div>
          </div>
          {unmatched.topSectors.map((s) => (
            <div key={s} className="flex flex-col justify-center rounded-[13px] border border-[#EBDCC9] bg-white px-[18px] py-[13px]">
              <div className="text-[14px] font-bold text-ink">{s}</div>
              <div className="mt-[4px] text-[11.5px] font-semibold text-[#9A8F7C]">частый сектор</div>
            </div>
          ))}
        </div>
        <div className="grid gap-[12px]" style={{ gridTemplateColumns: "repeat(auto-fill,minmax(250px,1fr))" }}>
          {samples.map((s) => (
            <div key={s.id} className="rounded-[15px] border border-[#EBDCC9] bg-white p-[16px]">
              <div className="text-[15.5px] font-bold tracking-[-.01em]">{s.name}</div>
              <div className="my-[7px] mb-[9px] text-[12px] font-semibold text-faint">{metaLine(s)}</div>
              <div className="text-[12.5px] leading-[1.45] text-prose">{clamp(s.description, 160)}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```
(Keep `C` import only if still referenced; otherwise drop it.)

- [ ] **Step 2: Wire into `App.tsx`**

Add `import UnmatchedSection from "./components/UnmatchedSection";` and remove the local `UnmatchedSection` function. Leave the `<UnmatchedSection unmatched={unmatched} onOpen={openUnmatched} />` usage as-is.

- [ ] **Step 3: Verify build + visual**

Run: `npm run build` then `npm run dev`. Expected: «Зона новых идей» block identical — badge, serif headline with count, paragraph, clay CTA with shadow, ПМО stat card + top-sector cards, 4 sample startup cards with clamped descriptions.

- [ ] **Step 4: Commit**

```bash
git add report-landing/src/components/UnmatchedSection.tsx report-landing/src/App.tsx
git commit -m "refactor(report): extract UnmatchedSection (tailwind), use shared clamp

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 11: Slim down & tailwindize `App.tsx` (main shell)

**Files:**
- Modify: `report-landing/src/App.tsx`

**Interfaces:**
- Consumes: all extracted components (Tasks 4-10), `LegendItem` from `./components/shared` (Task 3), `C`/`FONT_SERIF`/`statusMeta` from `./theme`.
- Produces: final `App` — state + the `shown`/`selection` memos + `<main>` composition only. No local view/section/`LegendItem`/`clampText`/`heroStats` definitions remain.

- [ ] **Step 1: Remove the now-duplicated local `LegendItem` and `clampText`**

Delete the local `function LegendItem(...)` and `function clampText(...)` from `App.tsx`. Add `LegendItem` to the shared import: `import { StatusBadge, metaLine, LegendItem } from "./components/shared";` (keep whatever of these `App` still uses — `App` uses `LegendItem`; `StatusBadge`/`metaLine` may now be unused in `App`, so remove them from the import if so).

- [ ] **Step 2: Tailwindize the `<main>` shell and heading/legend**

Replace the outer wrapper + `<main>` block. The root background stays inline-free via `bg-paper`:

```tsx
return (
  <div className="min-h-screen bg-paper">
    <Header />
    <Hero meta={meta} />
    <Controls view={view} setView={setView} status={status} setStatus={setStatus} minRel={minRel} setMinRel={setMinRel} q={q} setQ={setQ} sort={sort} setSort={setSort} dir={dir} setDir={setDir} />

    <main className="mx-auto max-w-[1240px] px-[28px] pb-[70px] pt-[30px]">
      <div className="mb-[20px] flex items-baseline justify-between gap-[16px]">
        <h2 className="m-0 text-[24px] font-normal tracking-[-.01em]" style={{ fontFamily: FONT_SERIF }}>
          <span className="font-bold">{meta.totalAgents}</span> Агента персонализированной модели образования
        </h2>
        <div className="text-[13px] font-medium text-muted">
          Показано <b className="text-ink">{shown.length}</b> из {meta.totalAgents}
        </div>
      </div>
      <div className="mb-[22px] flex flex-wrap items-center gap-[18px] text-[12px] font-semibold text-[#9A8F7C]">
        <LegendItem square color={C.clay} text="релевантность" />
        <LegendItem square color={C.teal} text="соответствие ПМО 2.0" />
        <LegendItem color="#3F7D55" text="в проде" />
        <LegendItem color="#A9781F" text="в разработке" />
      </div>

      {shown.length === 0 ? (
        <div className="px-[20px] py-[60px] text-center font-medium text-faint">
          Нет агентов под текущие фильтры
        </div>
      ) : view === "grid" ? (
        <GridView agents={shown} onOpen={openAgent} />
      ) : view === "compact" ? (
        <CompactView agents={shown} maxCount={maxCount} onOpen={openAgent} />
      ) : (
        <MapView agents={shown} maxCount={maxCount} onOpen={openAgent} />
      )}

      <UnmatchedSection unmatched={unmatched} onOpen={openUnmatched} />
    </main>

    <Drawer open={drawerOpen} selection={selection} minRel={minRel} dsort={dsort} onDsort={setDsort} onClose={() => setDrawerOpen(false)} onOpenInfo={setInfoAgent} />
    <AgentModal agent={infoAgent} onClose={() => setInfoAgent(null)} />
  </div>
);
```

Keep all imports actually used by the remaining code (`useEffect`, `useMemo`, `useState`, `reportData`, types, `enrich`, `C`, `FONT_SERIF`, `statusMeta`, the components, `Drawer`, `AgentModal`). Remove imports no longer referenced (e.g. `barW`, `fmt1`, `fmtInt` if they no longer appear in `App` — they moved into child components). Let `tsc` guide the cleanup.

- [ ] **Step 3: Verify build + visual**

Run: `npm run build` then `npm run dev`. Expected: full page identical end-to-end; section heading, legend (clay/teal squares, green/amber dots), empty-state message when filters exclude everything. `App.tsx` is now ~120 lines of state + composition.

- [ ] **Step 4: Commit**

```bash
git add report-landing/src/App.tsx
git commit -m "refactor(report): slim App.tsx to state + composition (tailwind shell)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 12: Tailwindize `Drawer.tsx`

**Files:**
- Modify: `report-landing/src/components/Drawer.tsx`
- Modify: `report-landing/src/index.css` (delete `.startup-link` and `.agent-title-link` rules)

**Interfaces:**
- Consumes: existing `DrawerSelection`/`DsortKey` types (unchanged), `C`/`FONT_SERIF`/`fmt1` from `../theme`, `StatusBadge`/`metaLine` from `./shared`, `clamp` from `../lib/text`.
- Produces: same `default export` and `DrawerSelection`/`DsortKey` exports — signature unchanged.

- [ ] **Step 1: Convert the overlay + panel**

Overlay `opacity`/`pointerEvents` and panel `transform` are driven by `open` → stay inline. The rest becomes utilities:

```tsx
<div
  onClick={onClose}
  aria-hidden
  className="fixed inset-0 z-[90] bg-[rgba(40,28,18,.34)] [backdrop-filter:blur(2px)] transition-opacity duration-[280ms]"
  style={{ opacity: open ? 1 : 0, pointerEvents: open ? "auto" : "none" }}
/>
<aside
  role="dialog"
  aria-modal="true"
  aria-label={selection?.name ?? "Группа"}
  className="fixed inset-y-0 right-0 z-[91] flex w-[min(760px,94vw)] flex-col bg-card-alt [box-shadow:-24px_0_60px_-30px_rgba(60,40,20,.5)] [transition:transform_.32s_cubic-bezier(.22,1,.36,1)]"
  style={{ transform: open ? "translateX(0)" : "translateX(100%)" }}
>
```

- [ ] **Step 2: Convert header, metrics-explainer, toolbar, list**

Apply the Conversion Reference to the remaining blocks. Key spots:
- Header wrapper: `className="border-b border-border bg-card px-[28px] pb-[18px] pt-[22px]"`.
- Close button: `className="flex h-[34px] w-[34px] cursor-pointer items-center justify-center rounded-full border border-border bg-white text-[17px] text-muted"`.
- The agent title link keeps `className="agent-title-link"` semantics as utilities: `className="cursor-pointer border-none bg-transparent p-0 text-left text-ink transition-colors duration-150 hover:text-clay hover:underline hover:[text-underline-offset:4px] hover:[text-decoration-thickness:1.5px] focus-visible:text-clay focus-visible:underline focus-visible:outline-none"` (font inherits via `style={{ fontFamily:"inherit", fontSize:"inherit", fontWeight:"inherit", letterSpacing:"inherit", lineHeight:"inherit" }}` kept inline since they inherit from the `<h2>`).
- `h2`: `className="m-0 mb-[8px] text-[30px] font-normal leading-[1.08] tracking-[-.015em]" style={{ fontFamily: FONT_SERIF }}`.
- Metrics-explainer dots use `bg-clay`/`bg-teal`.
- Toolbar select: same classes as `Controls` select.
- Scroll list wrapper: `className="flex-1 overflow-y-auto px-[28px] pb-[32px] pt-[6px]"`.

- [ ] **Step 3: Convert `StartupCard` and `ScoreBlock`; use shared `clamp`**

Replace `Drawer`'s local `clamp` with `import { clamp } from "../lib/text";` and delete the local `function clamp(...)`. In `StartupCard`:
- Card: `className="mb-[11px] rounded-[15px] border border-border-warm bg-white px-[17px] py-[16px]"`.
- The startup `<a>` keeps hover via utilities: `className="text-ink no-underline transition-colors duration-150 hover:text-clay hover:underline hover:[text-underline-offset:3px] focus-visible:text-clay focus-visible:underline focus-visible:outline-none"`.
- Sector chips: `className="rounded-[7px] border border-[#EBE0CE] bg-[#F4EEE2] px-[8px] py-[3px] text-[11px] font-semibold text-[#7A6E5B]"`.
- `rationale` block: `className="mt-[10px] border-l-2 border-[#E6CDB8] pl-[11px] text-[12.5px] italic leading-[1.5] text-[#9A8F7C]"`.
- `ScoreBlock` value: `className="text-[23px] leading-none [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF, color }}` (color runtime). Label: `style={{ color }}` kept, rest as classes.

- [ ] **Step 4: Delete dead CSS** — remove `.startup-link*` and `.agent-title-link*` rules from `src/index.css`.

- [ ] **Step 5: Verify build + visual**

Run: `npm run build` then `npm run dev`. Open a card → drawer slides in. Expected identical: header (category + badge + clickable serif title + description + prototype link), «О метриках» explainer, sort toolbar, startup cards (name link, meta line, sector chips, relevance/ПМО scores, description, italic rationale). Escape closes; clicking title opens the modal.

- [ ] **Step 6: Commit**

```bash
git add report-landing/src/components/Drawer.tsx report-landing/src/index.css
git commit -m "refactor(report): tailwindize Drawer, drop link hook css

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 13: Tailwindize `AgentModal.tsx`

**Files:**
- Modify: `report-landing/src/components/AgentModal.tsx`

**Interfaces:**
- Consumes: `Agent` from `../types`, `C`/`FONT_SERIF`/`statusMeta` from `../theme`, `StatusBadge` from `./shared`.
- Produces: same `default export function AgentModal({ agent, onClose })` — signature unchanged.

- [ ] **Step 1: Convert the backdrop + dialog shell**

Backdrop uses the `fadeIn` keyframe, dialog uses `fadeUp` — express via arbitrary `[animation:...]` (the keyframes live in `index.css`):

```tsx
<div onClick={onClose} className="fixed inset-0 z-[100] flex items-start justify-center overflow-y-auto bg-[rgba(40,28,18,.46)] px-[16px] py-[5vh] [backdrop-filter:blur(3px)] [animation:fadeIn_.2s_both]">
  <div role="dialog" aria-modal="true" aria-label={agent.name} onClick={(e) => e.stopPropagation()} className="w-[min(720px,100%)] overflow-hidden rounded-[22px] border border-border bg-card-alt [box-shadow:0_30px_80px_-30px_rgba(60,40,20,.6)] [animation:fadeUp_.26s_both]">
```

- [ ] **Step 2: Convert header + body + sub-components**

Apply the Conversion Reference:
- Header: `className="border-b border-border bg-card px-[30px] pb-[20px] pt-[24px]"`; close button identical to Drawer's; `h2` `className="m-0 mb-[8px] text-[28px] font-normal leading-[1.1] tracking-[-.015em]" style={{ fontFamily: FONT_SERIF }}`; resource link `className="mt-[14px] inline-block text-[12.5px] font-bold text-clay no-underline"`.
- Body wrapper: `className="px-[30px] pb-[30px] pt-[8px]"`.
- `Section` title: `className="mb-[10px] text-[11px] font-bold uppercase tracking-[.03em] text-faint"`; wrapper `className="pt-[18px]"`.
- userStory `<p>`: `className="m-0 border-l-2 border-clay pl-[13px] text-[14px] italic leading-[1.55] text-prose"`.
- functionalRequirements `<ul>`: `className="m-0 pl-[18px] text-[13.5px] leading-[1.6] text-ink-soft"`, `<li>` `className="mb-[4px]"`.
- `IOCard`: `className="rounded-[12px] border border-border-warm bg-white px-[14px] py-[12px]"`; label `className="mb-[6px] text-[10.5px] font-bold uppercase tracking-[.04em] text-faint"`; text `className="text-[13px] leading-[1.5] text-ink-soft"`.
- `CjmCard`: accent toggles background/border — keep those inline (`style={{ background: accent ? "#E7F0EC" : "#fff", borderColor: accent ? "#CFE2DA" : C.borderWarm }}`) on a `className="rounded-[13px] border px-[16px] py-[13px]"`; label color stays inline (`accent ? C.teal : "#9A6A4A"`).
- Input/output grid: `className="grid grid-cols-2 gap-[10px]"`; CJM grid: `className="grid grid-cols-1 gap-[10px]"`.

- [ ] **Step 3: Verify build + visual**

Run: `npm run build` then `npm run dev`. Open drawer → click agent title → modal. Expected identical: header (category + badge + serif name + role + prototype link), sections (user story italic with clay rule, functional requirements list, expected behavior, inputs/outputs grid, CJM cards with teal accent on platform card). Escape and backdrop-click close.

- [ ] **Step 4: Commit**

```bash
git add report-landing/src/components/AgentModal.tsx
git commit -m "refactor(report): tailwindize AgentModal

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 14: Final verification, doc update, and palette sync check

**Files:**
- Modify: `report-landing/README.md` (structure section)

**Interfaces:**
- Consumes: the whole migrated module.
- Produces: updated README structure tree + Tailwind in the stack list.

- [ ] **Step 1: Full clean build**

Run: `cd report-landing && rm -rf dist && npm run build`
Expected: `tsc -b` reports no errors and `vite build` writes `dist/`. The CSS bundle now contains Tailwind utilities.

- [ ] **Step 2: Grep for leftover inline-style sprawl and dead CSS**

Run: `grep -rn "style={{" src/ | wc -l`
Expected: a small number — only the runtime cases listed in the Conversion Reference (bar widths, status colors, tile size, drawer transforms, gradients, inherited fonts). No static layout `style` blocks should remain.

Run: `grep -rn "agent-card\|agent-row\|agent-tile\|startup-link\|agent-title-link" src/`
Expected: no matches (all hook classes removed).

- [ ] **Step 3: Confirm palette parity between `@theme` and `C`**

Visually diff the hex values in `index.css` `@theme` against `theme.ts` `C`. Every `C` value must have a matching `--color-*`. Expected: identical hexes.

- [ ] **Step 4: Visual regression pass in dev**

Run: `npm run dev`. Walk the full checklist: Header · Hero (6 stats) · Controls (toggle/chips/slider/search/sort) · Grid view · Compact view · Map view · empty-state · Unmatched section · Drawer (agent + «Новые идеи») · AgentModal · keyboard (Escape), scroll-lock under drawer, `prefers-reduced-motion`. Compare against the pre-migration look — must be pixel-identical.

- [ ] **Step 5: Update README**

In `report-landing/README.md`: add Tailwind to the stack list (e.g. under «Стек»: `- **Tailwind CSS v4** — оформление через утилиты + @theme-токены (CSS-first конфиг в index.css)`), and update the «Структура» tree to show `components/Header.tsx`, `Hero.tsx`, `Controls.tsx`, `UnmatchedSection.tsx`, `views/{Grid,Compact,Map}View.tsx`, `lib/text.ts`, and note `index.css` holds `@theme` + неутилитный CSS.

- [ ] **Step 6: Commit**

```bash
git add report-landing/README.md
git commit -m "docs(report): document Tailwind v4 + new component structure

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:**
- Tailwind v4 + `@tailwindcss/vite` + `@theme` → Task 1. ✓
- Palette tokens mirror `C` → Task 1 (`@theme`), parity checked Task 14 Step 3. ✓
- Pixel-perfect via arbitrary values → Conversion Reference + every conversion task. ✓
- Runtime styles stay inline → Conversion Reference + called out per task (Controls, Compact/Map views, Drawer, Modal). ✓
- Split `App.tsx` into Header/Hero/Controls/views/UnmatchedSection → Tasks 4-11. ✓
- Shared `clamp` in `lib/text.ts` → Task 2, consumed Tasks 10 & 12. ✓
- Remove dead `Bar`/`pill`/`FONT_SANS` → Task 2. ✓
- Keep non-utility CSS (slider, scrollbar, selection, keyframes, reduced-motion) → Task 1; hook classes removed per-component (Tasks 7-9, 12). ✓
- No new test runtime; build + visual gate → every task. ✓
- README/structure update → Task 14. ✓
- Scope limited to `report-landing/` → Global Constraints; `lib/report.ts`/`types.ts`/`data`/`scripts` untouched. ✓

**Placeholder scan:** No TBD/TODO; each conversion task ships concrete code or a precise per-element class mapping grounded in the Conversion Reference. ✓

**Type consistency:** `clamp(text, max)` signature consistent across `lib/text.ts`, `UnmatchedSection`, `Drawer`. `View`/`SortKey` exported from `Controls` and imported by `App`. `UnmatchedBucket` (from `lib/report`) replaces the inferred type in `UnmatchedSection`. View component prop shapes match `App`'s call sites. ✓
