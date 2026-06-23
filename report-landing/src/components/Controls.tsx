import { useLayoutEffect, useRef, useState } from "react";
import { C } from "../theme";
import {
  IDEA_SORTS,
  PMO_SORTS,
  STATUS_CHIPS,
  VIEWS,
  ideaHasFilters,
  pmoHasFilters,
  type IdeaControls,
  type IdeaSort,
  type PmoControls,
  type PmoSort,
  type View,
} from "./filterDefs";

const SearchIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#A9997F" strokeWidth="2.2">
    <circle cx="11" cy="11" r="7" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

const FilterIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
    <line x1="4" y1="6" x2="20" y2="6" />
    <line x1="7" y1="12" x2="17" y2="12" />
    <line x1="10" y1="18" x2="14" y2="18" />
  </svg>
);

const selectCls =
  "cursor-pointer rounded-full border border-border bg-white px-[13px] py-[8px] text-[12.5px] font-semibold text-[#4A4339] outline-none";

export default function Controls({
  view,
  setView,
  ctrlStuck,
  pmo,
  ideas,
  openFilters,
}: {
  view: View;
  setView: (v: View) => void;
  ctrlStuck: boolean;
  pmo: PmoControls;
  ideas: IdeaControls;
  openFilters: () => void;
}) {
  const segRef = useRef<HTMLDivElement>(null);
  const [pill, setPill] = useState({ x: 0, w: 0, ready: false });

  useLayoutEffect(() => {
    const measure = () => {
      const wrap = segRef.current;
      if (!wrap) return;
      const idx = VIEWS.findIndex((v) => v.k === view);
      const btn = wrap.querySelectorAll("button")[idx] as HTMLButtonElement | undefined;
      if (!btn) return;
      setPill({ x: btn.offsetLeft - wrap.clientLeft, w: btn.offsetWidth, ready: true });
    };
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [view]);

  return (
    <div
      data-ctrlbar
      className="sticky top-[50px] z-40 transition-[background-color,backdrop-filter] duration-[250ms] md:top-[53px]"
      style={{
        background: ctrlStuck ? "rgba(244,238,228,.82)" : "transparent",
        backdropFilter: ctrlStuck ? "blur(16px)" : "blur(0px)",
        WebkitBackdropFilter: ctrlStuck ? "blur(16px)" : "blur(0px)",
      }}
    >
      <div className="mx-auto flex max-w-[1240px] flex-col gap-[10px] px-[18px] py-[11px] md:flex-row md:flex-wrap md:items-center md:gap-[14px] md:px-[28px] md:py-[14px]">
        {/* segmented view switch */}
        <div
          ref={segRef}
          className="relative flex w-full gap-[4px] rounded-full border border-[#E1D6C2] bg-[#EBE2D2] p-[4px] md:w-auto"
        >
          <div
            aria-hidden
            className="pointer-events-none absolute bottom-[4px] left-0 top-[4px] z-0 rounded-full bg-ink"
            style={{
              transform: `translateX(${pill.x}px)`,
              width: pill.w,
              opacity: pill.ready ? 1 : 0,
              transition: "transform .42s cubic-bezier(.22,.61,.36,1), width .42s cubic-bezier(.22,.61,.36,1), opacity .2s",
            }}
          />
          {VIEWS.map((v) => (
            <button
              key={v.k}
              onClick={() => setView(v.k)}
              className="relative z-[1] flex-1 cursor-pointer whitespace-nowrap rounded-full border-none bg-transparent px-[4px] py-[9px] text-[13px] font-bold transition-colors duration-300 md:flex-none md:px-[16px] md:py-[7px] md:font-semibold"
              style={{ color: view === v.k ? "#fff" : C.muted }}
            >
              <span className="md:hidden">{v.short}</span>
              <span className="hidden md:inline">{v.full}</span>
            </button>
          ))}
        </div>

        {view === "pmo" && (
          <>
            <DesktopPmoFilters pmo={pmo} />
            <MobileSearchRow
              value={pmo.q}
              onChange={pmo.setQ}
              placeholder="Поиск агента…"
              active={pmoHasFilters(pmo)}
              accent={C.clay}
              openFilters={openFilters}
            />
          </>
        )}

        {view === "ideas" && (
          <>
            <DesktopIdeaFilters ideas={ideas} />
            <MobileSearchRow
              value={ideas.q}
              onChange={ideas.setQ}
              placeholder="Поиск стартапа…"
              active={ideaHasFilters(ideas)}
              accent={C.teal}
              openFilters={openFilters}
            />
          </>
        )}
      </div>
    </div>
  );
}

function DesktopPmoFilters({ pmo }: { pmo: PmoControls }) {
  return (
    <div className="hidden basis-full flex-wrap items-center gap-[14px] md:flex">
      <div className="flex flex-wrap items-center gap-[8px]">
        {STATUS_CHIPS.map((c) => {
          const on = pmo.status === c.v;
          return (
            <button
              key={c.v}
              onClick={() => pmo.setStatus(c.v)}
              className="inline-flex cursor-pointer items-center gap-[7px] rounded-full border px-[13px] py-[7px] text-[12.5px] font-semibold transition-all duration-150"
              style={{ borderColor: on ? C.ink : C.border, background: on ? C.ink : "#fff", color: on ? "#fff" : "#4A4339" }}
            >
              <span className="h-[7px] w-[7px] rounded-full" style={{ background: on ? (c.v === "all" ? "#fff" : c.dot) : c.dot }} />
              {c.label}
            </button>
          );
        })}
      </div>

      <div className="flex items-center gap-[11px] rounded-full border border-border bg-white px-[15px] py-[7px]">
        <span className="whitespace-nowrap text-[12.5px] font-semibold text-muted">Релевантность ≥</span>
        <input
          type="range"
          min={0}
          max={9}
          step={1}
          value={pmo.minRel}
          onChange={(e) => pmo.setMinRel(Number(e.target.value))}
          className="w-[108px]"
          aria-label="Минимальная релевантность"
        />
        <span className="min-w-[34px] text-[12.5px] font-bold text-clay [font-variant-numeric:tabular-nums]">
          {pmo.minRel === 0 ? "любая" : pmo.minRel}
        </span>
      </div>

      <div className="flex-1" />

      <div className="relative flex items-center rounded-full border border-border bg-white pl-[14px] pr-[6px]">
        <SearchIcon />
        <input
          type="text"
          value={pmo.q}
          onChange={(e) => pmo.setQ(e.target.value)}
          placeholder="Поиск агента…"
          aria-label="Поиск агента"
          className="w-[140px] border-none bg-transparent px-[8px] py-[8px] text-[13px] text-ink outline-none"
        />
      </div>

      <div className="flex items-center gap-[6px]">
        <select value={pmo.sort} onChange={(e) => pmo.setSort(e.target.value as PmoSort)} aria-label="Сортировка" className={selectCls}>
          {PMO_SORTS.map((s) => (
            <option key={s.v} value={s.v}>
              {s.label}
            </option>
          ))}
        </select>
        <button
          onClick={() => pmo.setDir(pmo.dir === "asc" ? "desc" : "asc")}
          title="Направление"
          aria-label="Направление сортировки"
          className="flex h-[34px] w-[34px] cursor-pointer items-center justify-center rounded-full border border-border bg-white text-[14px] text-[#4A4339]"
        >
          {pmo.dir === "asc" ? "↑" : "↓"}
        </button>
      </div>
    </div>
  );
}

function DesktopIdeaFilters({ ideas }: { ideas: IdeaControls }) {
  return (
    <div className="hidden basis-full flex-wrap items-center gap-[10px] md:flex">
      <select value={ideas.sector} onChange={(e) => ideas.setSector(e.target.value)} aria-label="Сектор" className={selectCls}>
        <option value="all">Все секторы</option>
        {ideas.sectors.map((x) => (
          <option key={x} value={x}>
            {x}
          </option>
        ))}
      </select>
      <select value={ideas.fund} onChange={(e) => ideas.setFund(e.target.value)} aria-label="Фонд" className={selectCls}>
        <option value="all">Все фонды</option>
        {ideas.funds.map((x) => (
          <option key={x} value={x}>
            {x}
          </option>
        ))}
      </select>
      <select value={ideas.stage} onChange={(e) => ideas.setStage(e.target.value)} aria-label="Стадия" className={selectCls}>
        <option value="all">Все стадии</option>
        {ideas.stages.map((x) => (
          <option key={x} value={x}>
            {x}
          </option>
        ))}
      </select>

      <div className="flex-1" />

      <div className="relative flex items-center rounded-full border border-border bg-white pl-[14px] pr-[6px]">
        <SearchIcon />
        <input
          type="text"
          value={ideas.q}
          onChange={(e) => ideas.setQ(e.target.value)}
          placeholder="Поиск стартапа…"
          aria-label="Поиск стартапа"
          className="w-[150px] border-none bg-transparent px-[8px] py-[8px] text-[13px] text-ink outline-none"
        />
      </div>

      <select value={ideas.sort} onChange={(e) => ideas.setSort(e.target.value as IdeaSort)} aria-label="Сортировка" className={selectCls}>
        {IDEA_SORTS.map((s) => (
          <option key={s.v} value={s.v}>
            {s.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function MobileSearchRow({
  value,
  onChange,
  placeholder,
  active,
  accent,
  openFilters,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  active: boolean;
  accent: string;
  openFilters: () => void;
}) {
  return (
    <div className="flex items-center gap-[9px] md:hidden">
      <div className="flex flex-1 items-center rounded-full border border-border bg-white pl-[13px] pr-[6px]">
        <SearchIcon />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full border-none bg-transparent px-[8px] py-[10px] text-[14px] text-ink outline-none"
        />
      </div>
      <button
        onClick={openFilters}
        className="relative inline-flex flex-none cursor-pointer items-center gap-[7px] rounded-full border px-[14px] py-[10px] text-[13px] font-bold"
        style={{ borderColor: active ? C.ink : C.border, background: active ? C.ink : "#fff", color: active ? "#fff" : "#4A4339" }}
      >
        <FilterIcon />
        Фильтры
        {active && <span className="h-[7px] w-[7px] rounded-full" style={{ background: accent }} />}
      </button>
    </div>
  );
}
