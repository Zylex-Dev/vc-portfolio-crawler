import { C } from "../theme";
import {
  IDEA_SORTS,
  PMO_SORTS,
  STATUS_CHIPS,
  type IdeaControls,
  type IdeaSort,
  type PmoControls,
  type PmoSort,
} from "./filterDefs";

const selectCls =
  "w-full cursor-pointer rounded-[12px] border border-border bg-white px-[13px] py-[12px] text-[14px] font-semibold text-[#4A4339] outline-none";
const labelCls = "mb-[9px] text-[11px] font-bold uppercase tracking-[.03em] text-faint";

/** Mobile-only bottom sheet mirroring the desktop filter bar. */
export default function FilterSheet({
  open,
  view,
  pmo,
  ideas,
  onClose,
  onReset,
}: {
  open: boolean;
  view: "pmo" | "ideas";
  pmo: PmoControls;
  ideas: IdeaControls;
  onClose: () => void;
  onReset: () => void;
}) {
  return (
    <div className="md:hidden">
      <div
        onClick={onClose}
        aria-hidden
        className="fixed inset-0 z-[80] bg-[rgba(40,28,18,.34)] transition-opacity duration-[260ms]"
        style={{ opacity: open ? 1 : 0, pointerEvents: open ? "auto" : "none" }}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Фильтры и сортировка"
        className="fixed bottom-0 left-0 right-0 z-[81] mx-auto max-h-[86vh] max-w-[430px] overflow-y-auto rounded-t-[22px] bg-card-alt px-[18px] pb-[26px] pt-[8px] [box-shadow:0_-16px_40px_-20px_rgba(60,40,20,.5)] [transition:transform_.3s_cubic-bezier(.22,1,.36,1)]"
        style={{ transform: open ? "translateY(0)" : "translateY(100%)" }}
      >
        <div className="mx-auto mb-[16px] mt-[8px] h-[4px] w-[38px] rounded-full bg-[#D8CCB8]" />
        <div className="mb-[18px] flex items-center justify-between">
          <div className="text-[21px]" style={{ fontFamily: "'Newsreader',serif" }}>
            Фильтры и сортировка
          </div>
          <button onClick={onReset} className="cursor-pointer border-none bg-transparent text-[13px] font-bold text-clay">
            Сбросить
          </button>
        </div>

        {view === "pmo" ? (
          <>
            <div className={labelCls}>Статус</div>
            <div className="mb-[22px] flex flex-wrap gap-[7px]">
              {STATUS_CHIPS.map((c) => {
                const on = pmo.status === c.v;
                return (
                  <button
                    key={c.v}
                    onClick={() => pmo.setStatus(c.v)}
                    className="inline-flex cursor-pointer items-center gap-[7px] rounded-full border px-[14px] py-[9px] text-[13px] font-semibold"
                    style={{ borderColor: on ? C.ink : C.border, background: on ? C.ink : "#fff", color: on ? "#fff" : "#4A4339" }}
                  >
                    <span className="h-[7px] w-[7px] rounded-full" style={{ background: on ? (c.v === "all" ? "#fff" : c.dot) : c.dot }} />
                    {c.label}
                  </button>
                );
              })}
            </div>

            <div className="mb-[10px] flex items-center justify-between">
              <span className={labelCls + " mb-0"}>Релевантность ≥</span>
              <span className="text-[14px] font-bold text-clay [font-variant-numeric:tabular-nums]">{pmo.minRel === 0 ? "любая" : pmo.minRel}</span>
            </div>
            <input
              type="range"
              min={0}
              max={9}
              step={1}
              value={pmo.minRel}
              onChange={(e) => pmo.setMinRel(Number(e.target.value))}
              className="mb-[22px] w-full"
              aria-label="Минимальная релевантность"
            />

            <div className={labelCls}>Сортировка</div>
            <div className="mb-[14px] flex flex-wrap gap-[7px]">
              {PMO_SORTS.map((s) => (
                <SortChip key={s.v} label={s.label} on={pmo.sort === s.v} onClick={() => pmo.setSort(s.v as PmoSort)} />
              ))}
            </div>
            <button
              onClick={() => pmo.setDir(pmo.dir === "asc" ? "desc" : "asc")}
              className="mb-[24px] inline-flex cursor-pointer items-center gap-[8px] rounded-full border border-border bg-white px-[16px] py-[9px] text-[13px] font-semibold text-[#4A4339]"
            >
              Направление {pmo.dir === "asc" ? "↑" : "↓"}
            </button>
          </>
        ) : (
          <>
            <div className={labelCls}>Сектор</div>
            <select value={ideas.sector} onChange={(e) => ideas.setSector(e.target.value)} className={selectCls + " mb-[16px]"}>
              <option value="all">Все секторы</option>
              {ideas.sectors.map((x) => (
                <option key={x} value={x}>
                  {x}
                </option>
              ))}
            </select>
            <div className={labelCls}>Фонд</div>
            <select value={ideas.fund} onChange={(e) => ideas.setFund(e.target.value)} className={selectCls + " mb-[16px]"}>
              <option value="all">Все фонды</option>
              {ideas.funds.map((x) => (
                <option key={x} value={x}>
                  {x}
                </option>
              ))}
            </select>
            <div className={labelCls}>Стадия</div>
            <select value={ideas.stage} onChange={(e) => ideas.setStage(e.target.value)} className={selectCls + " mb-[20px]"}>
              <option value="all">Все стадии</option>
              {ideas.stages.map((x) => (
                <option key={x} value={x}>
                  {x}
                </option>
              ))}
            </select>
            <div className={labelCls}>Сортировка</div>
            <div className="mb-[24px] flex flex-wrap gap-[7px]">
              {IDEA_SORTS.map((s) => (
                <SortChip key={s.v} label={s.label} on={ideas.sort === s.v} onClick={() => ideas.setSort(s.v as IdeaSort)} />
              ))}
            </div>
          </>
        )}

        <button
          onClick={onClose}
          className="w-full cursor-pointer rounded-[13px] border-none bg-ink px-[15px] py-[15px] text-[15px] font-bold text-white"
        >
          Готово
        </button>
      </div>
    </div>
  );
}

function SortChip({ label, on, onClick }: { label: string; on: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="cursor-pointer rounded-full border px-[14px] py-[9px] text-[13px] font-semibold"
      style={{ borderColor: on ? C.ink : C.border, background: on ? C.ink : "#fff", color: on ? "#fff" : "#4A4339" }}
    >
      {label}
    </button>
  );
}
