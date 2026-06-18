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
