import { useMemo } from "react";
import type { Agent, PmoSub, Startup } from "../types";
import { FONT_SERIF, fmt1 } from "../theme";
import { StatusBadge, metaLine } from "./shared";
import { clamp } from "../lib/text";

export interface DrawerSelection {
  kind: "agent" | "unmatched";
  name: string;
  category: string;
  status: { label: string; color: string; bg: string };
  sredstvo: string;
  description: string;
  count: number;
  avgRel: number;
  avgPmo: number;
  sub: PmoSub;
  group: Startup[];
  agent?: Agent;
}

const DSORT = {
  relevance: (s: Startup) => s.relevance,
  pmo: (s: Startup) => s.pmoScore,
  year: (s: Startup) => s.foundedYear ?? 0,
  name: (s: Startup) => s.name,
} as const;

export type DsortKey = keyof typeof DSORT;

export default function Drawer({
  open,
  selection,
  minRel,
  dsort,
  onDsort,
  onClose,
  onOpenInfo,
}: {
  open: boolean;
  selection: DrawerSelection | null;
  minRel: number;
  dsort: DsortKey;
  onDsort: (v: DsortKey) => void;
  onClose: () => void;
  onOpenInfo: (agent: Agent) => void;
}) {
  const startups = useMemo(() => {
    if (!selection) return [];
    const f = DSORT[dsort] ?? DSORT.relevance;
    return [...selection.group]
      .filter((s) => s.relevance >= minRel)
      .sort((a, b) => {
        const xa = f(a);
        const ya = f(b);
        if (typeof xa === "string" && typeof ya === "string") return xa.localeCompare(ya, "ru");
        return (ya as number) - (xa as number);
      });
  }, [selection, dsort, minRel]);

  return (
    <>
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
        {selection && (
          <>
            {/* header */}
            <div className="border-b border-border bg-card px-[28px] pb-[18px] pt-[22px]">
              <div className="flex items-center justify-between gap-[12px] mb-[14px]">
                <div className="flex items-center gap-[9px]">
                  <span className="text-[11px] font-bold uppercase tracking-[.03em] text-faint">
                    {selection.category}
                  </span>
                  <StatusBadge label={selection.status.label} color={selection.status.color} bg={selection.status.bg} small />
                </div>
                <button
                  onClick={onClose}
                  aria-label="Закрыть"
                  className="flex h-[34px] w-[34px] cursor-pointer items-center justify-center rounded-full border border-border bg-white text-[17px] text-muted"
                >
                  ✕
                </button>
              </div>
              <h2
                className="m-0 mb-[8px] text-[30px] font-normal leading-[1.08] tracking-[-.015em]"
                style={{ fontFamily: FONT_SERIF }}
              >
                {selection.kind === "agent" && selection.agent ? (
                  <button
                    onClick={() => onOpenInfo(selection.agent!)}
                    title="Открыть подробную информацию об агенте"
                    className="cursor-pointer border-none bg-transparent p-0 text-left text-ink transition-colors duration-150 hover:text-clay hover:underline hover:[text-underline-offset:4px] hover:[text-decoration-thickness:1.5px] focus-visible:text-clay focus-visible:underline focus-visible:outline-none"
                    style={{ fontFamily: "inherit", fontSize: "inherit", fontWeight: "inherit", letterSpacing: "inherit", lineHeight: "inherit" }}
                  >
                    {selection.name}
                  </button>
                ) : (
                  selection.name
                )}
              </h2>
              <p className="m-0 text-[14px] leading-[1.5] text-prose max-w-[64ch]">{selection.description}</p>
              {selection.kind === "agent" && selection.agent?.resourceLink && (
                <a
                  href={selection.agent.resourceLink}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block mt-[12px] text-[12.5px] font-bold text-clay no-underline"
                >
                  Открыть прототип агента →
                </a>
              )}
            </div>

            {/* how to read the metrics */}
            <div className="border-b border-border px-[28px] py-[18px]">
              <div className="text-[11px] font-bold uppercase tracking-[.03em] text-faint mb-[12px]">
                О метриках
              </div>
              <div className="flex flex-col gap-[12px]">
                <div className="flex gap-[11px]">
                  <span className="mt-[5px] h-[9px] w-[9px] shrink-0 rounded-[2px] bg-clay" />
                  <div>
                    <div className="text-[13.5px] font-bold text-ink mb-[2px]">Релевантность</div>
                    <div className="text-[13px] leading-[1.5] text-prose">
                      Насколько продукт стартапа близок к задаче этого агента — то есть к тому, что строим мы.
                      Шкала 0–10: чем выше, тем сильнее пересечение с нашим направлением.
                    </div>
                  </div>
                </div>
                <div className="flex gap-[11px]">
                  <span className="mt-[5px] h-[9px] w-[9px] shrink-0 rounded-[2px] bg-teal" />
                  <div>
                    <div className="text-[13.5px] font-bold text-ink mb-[2px]">Соответствие ПМО 2.0</div>
                    <div className="text-[13px] leading-[1.5] text-prose">
                      Насколько решение опирается на принципы персонализированной модели образования:
                      траекторию, материалы, коллаборацию, геймификацию и обратную связь.
                      Шкала 0–10: чем выше, тем зрелее продукт с точки зрения ПМО.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* list toolbar */}
            <div className="flex items-center justify-between gap-[12px] px-[28px] pt-[14px] pb-[10px]">
              <div className="text-[13px] font-semibold text-muted">
                Стартапы группы · <b className="text-ink">{startups.length}</b>
              </div>
              <div className="flex items-center gap-[7px]">
                <span className="text-[12px] font-semibold text-faint">Сортировка</span>
                <select
                  value={dsort}
                  onChange={(e) => onDsort(e.target.value as DsortKey)}
                  className="border border-border bg-white rounded-full px-[12px] py-[7px] text-[12.5px] font-semibold text-[#4A4339] cursor-pointer outline-none"
                >
                  <option value="relevance">релевантность</option>
                  <option value="pmo">соответствие ПМО 2.0</option>
                  <option value="year">год основания</option>
                  <option value="name">название</option>
                </select>
              </div>
            </div>

            {/* startup cards */}
            <div className="flex-1 overflow-y-auto px-[28px] pb-[32px] pt-[6px]">
              {startups.map((s) => (
                <StartupCard key={s.id} s={s} />
              ))}
              {startups.length === 0 && (
                <div className="text-center px-[20px] py-[40px] text-faint font-medium">
                  Нет данных по стартапам
                </div>
              )}
            </div>
          </>
        )}
      </aside>
    </>
  );
}

function StartupCard({ s }: { s: Startup }) {
  return (
    <div className="mb-[11px] rounded-[15px] border border-border-warm bg-white px-[17px] py-[16px]">
      <div className="flex items-start justify-between gap-[16px]">
        <div className="min-w-0">
          <div className="text-[16px] font-bold tracking-[-.01em]">
            {s.website ? (
              <a
                href={s.website}
                target="_blank"
                rel="noreferrer"
                className="text-ink no-underline transition-colors duration-150 hover:text-clay hover:underline hover:[text-underline-offset:3px] focus-visible:text-clay focus-visible:underline focus-visible:outline-none"
              >
                {s.name}
              </a>
            ) : (
              s.name
            )}
          </div>
          <div className="flex items-center flex-wrap gap-[6px] mt-[6px]">
            <span className="text-[12px] font-semibold text-faint">{metaLine(s)}</span>
            {s.sectors.map((t) => (
              <span key={t} className="rounded-[7px] border border-[#EBE0CE] bg-[#F4EEE2] px-[8px] py-[3px] text-[11px] font-semibold text-[#7A6E5B]">
                {t}
              </span>
            ))}
          </div>
        </div>
        <div className="flex items-start gap-[18px] shrink-0">
          <ScoreBlock label="Релевантность" value={s.relevance} color="#C2603C" />
          <ScoreBlock label="ПМО" value={s.pmoScore} color="#3F8A78" />
        </div>
      </div>

      {s.description && <div className="text-[13px] text-ink-soft leading-[1.5] mt-[11px]">{clamp(s.description, 320)}</div>}
      {s.rationale && (
        <div className="mt-[10px] border-l-2 border-[#E6CDB8] pl-[11px] text-[12.5px] italic leading-[1.5] text-[#9A8F7C]">
          {s.rationale}
        </div>
      )}
    </div>
  );
}

function ScoreBlock({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex flex-col items-start gap-[2px]">
      <span
        className="text-[23px] leading-none [font-variant-numeric:tabular-nums]"
        style={{ fontFamily: FONT_SERIF, color }}
      >
        {fmt1(value)}
      </span>
      <span
        className="text-[9.5px] font-bold uppercase tracking-[.03em] whitespace-nowrap"
        style={{ color }}
      >
        {label}
      </span>
    </div>
  );
}
