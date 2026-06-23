import { useMemo } from "react";
import type { Agent, AgentGroup, Startup } from "../types";
import { FONT_SERIF, SCORE_LABEL, fmt1 } from "../theme";
import { metaLine } from "./shared";
import { DSORTS, type Dsort } from "./filterDefs";

const DSORT_FN = {
  relevance: (s: Startup) => s.relevance,
  pmo: (s: Startup) => s.pmoScore,
  year: (s: Startup) => s.foundedYear ?? 0,
  name: (s: Startup) => s.name,
} as const;

const webHost = (url: string) => url.replace(/^https?:\/\//, "").replace(/\/$/, "");
const webHref = (url: string) => (/^https?:\/\//.test(url) ? url : `https://${url}`);

export default function Drawer({
  open,
  kind,
  agent,
  idea,
  dsort,
  onDsort,
  minRel,
  onClose,
  onOpenInfo,
}: {
  open: boolean;
  kind: "agent" | "idea" | null;
  agent: AgentGroup | null;
  idea: Startup | null;
  dsort: Dsort;
  onDsort: (v: Dsort) => void;
  minRel: number;
  onClose: () => void;
  onOpenInfo: (a: Agent) => void;
}) {
  const startups = useMemo(() => {
    if (!agent) return [];
    const f = DSORT_FN[dsort] ?? DSORT_FN.relevance;
    return [...agent.group]
      .filter((s) => s.relevance >= minRel)
      .sort((a, b) => {
        const xa = f(a);
        const ya = f(b);
        if (typeof xa === "string" && typeof ya === "string") return xa.localeCompare(ya, "ru");
        return (ya as number) - (xa as number);
      });
  }, [agent, dsort, minRel]);

  const title = kind === "agent" ? agent?.name : idea?.name;

  return (
    <>
      <div
        onClick={onClose}
        aria-hidden
        className="fixed inset-0 z-[90] hidden bg-[rgba(40,28,18,.34)] [backdrop-filter:blur(2px)] transition-opacity duration-[280ms] md:block"
        style={{ opacity: open ? 1 : 0, pointerEvents: open ? "auto" : "none" }}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={title ?? "Детали"}
        className="fixed inset-0 z-[91] flex flex-col bg-card-alt [transition:transform_.32s_cubic-bezier(.22,1,.36,1)] md:inset-y-0 md:left-auto md:right-0 md:w-[min(760px,94vw)] md:[box-shadow:-24px_0_60px_-30px_rgba(60,40,20,.5)]"
        style={{ transform: open ? "translateX(0)" : "translateX(100%)" }}
      >
        {/* header */}
        <div className="relative flex-none border-b border-border bg-card px-[18px] pb-[16px] pt-[14px] md:px-[28px] md:pb-[20px] md:pt-[22px]">
          <button
            onClick={onClose}
            className="mb-[13px] inline-flex cursor-pointer items-center gap-[6px] rounded-full border border-border bg-white px-[14px] py-[8px] text-[13px] font-bold text-muted md:hidden"
          >
            ← Назад
          </button>
          <button
            onClick={onClose}
            aria-label="Закрыть"
            className="absolute right-[24px] top-[18px] hidden h-[34px] w-[34px] cursor-pointer items-center justify-center rounded-full border border-border bg-white text-[17px] text-muted md:flex"
          >
            ✕
          </button>

          <h2
            className="m-0 mb-[8px] text-[25px] font-normal leading-[1.1] tracking-[-.015em] md:mr-[48px] md:text-[30px] md:leading-[1.08]"
            style={{ fontFamily: FONT_SERIF }}
          >
            {kind === "agent" && agent ? (
              <button
                onClick={() => onOpenInfo(agent)}
                title="Открыть подробную информацию об агенте"
                className="cursor-pointer border-none bg-transparent p-0 text-left text-ink transition-colors duration-150 hover:text-clay hover:underline hover:[text-decoration-thickness:1.5px] hover:[text-underline-offset:4px] focus-visible:text-clay focus-visible:underline focus-visible:outline-none"
                style={{ fontFamily: "inherit", fontSize: "inherit", fontWeight: "inherit", letterSpacing: "inherit", lineHeight: "inherit" }}
              >
                {agent.name}
              </button>
            ) : (
              title
            )}
          </h2>

          {kind === "agent" && agent && (
            <>
              {agent.role && <p className="m-0 max-w-[64ch] text-[13.5px] leading-[1.5] text-prose md:text-[14px]">{agent.role}</p>}
              {agent.resourceLink && (
                <a
                  href={agent.resourceLink}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-[12px] inline-block text-[13px] font-bold text-clay no-underline md:text-[12.5px]"
                >
                  Открыть прототип агента →
                </a>
              )}
            </>
          )}

          {kind === "idea" && idea && (
            <>
              {idea.description && <p className="m-0 mb-[14px] max-w-[64ch] text-[13.5px] leading-[1.5] text-prose md:text-[14px]">{idea.description}</p>}
              <div className="flex flex-wrap gap-[8px]">
                {idea.website && (
                  <a
                    href={webHref(idea.website)}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-[7px] rounded-full border border-[#D8CBB6] px-[15px] py-[7px] text-[12.5px] font-semibold text-[#4A4339] no-underline"
                  >
                    ↗ {webHost(idea.website)}
                  </a>
                )}
                {idea.sectors.map((t) => (
                  <span key={t} className="rounded-full border border-[#EBE0CE] bg-[#F4EEE2] px-[14px] py-[7px] text-[12px] font-semibold text-[#7A6E5B]">
                    {t}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>

        {/* body (scrolls) */}
        <div className="flex-1 overflow-y-auto">
          <MetricsBlock />

          {kind === "agent" && agent && (
            <>
              <div className="flex items-center justify-between gap-[10px] px-[18px] pb-[12px] pt-[16px] md:px-[28px] md:pb-[10px] md:pt-[14px]">
                <div className="text-[13px] font-bold text-ink md:font-semibold md:text-muted">
                  Стартапы<span className="hidden md:inline"> группы</span> · <b className="text-ink">{startups.length}</b>
                </div>
                {/* desktop select */}
                <div className="hidden items-center gap-[7px] md:flex">
                  <span className="text-[12px] font-semibold text-faint">Сортировка</span>
                  <select
                    value={dsort}
                    onChange={(e) => onDsort(e.target.value as Dsort)}
                    className="cursor-pointer rounded-full border border-border bg-white px-[12px] py-[7px] text-[12.5px] font-semibold text-[#4A4339] outline-none"
                  >
                    {DSORTS.map((d) => (
                      <option key={d.v} value={d.v}>
                        {d.label}
                      </option>
                    ))}
                  </select>
                </div>
                {/* mobile chips */}
                <div className="noscroll flex max-w-[62%] gap-[6px] overflow-x-auto md:hidden">
                  {DSORTS.map((d) => {
                    const on = dsort === d.v;
                    return (
                      <button
                        key={d.v}
                        onClick={() => onDsort(d.v)}
                        className="flex-none cursor-pointer rounded-full border px-[11px] py-[6px] text-[11.5px] font-semibold"
                        style={{ borderColor: on ? "#211C16" : "#E7DECF", background: on ? "#211C16" : "#fff", color: on ? "#fff" : "#4A4339" }}
                      >
                        {d.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex flex-col gap-[10px] px-[18px] pb-[30px] pt-[6px] md:gap-[12px] md:px-[28px] md:pb-[32px]">
                {startups.map((s) => (
                  <StartupCard key={s.id} s={s} />
                ))}
                {startups.length === 0 && (
                  <div className="px-[20px] py-[40px] text-center font-medium text-faint">Нет данных по стартапам</div>
                )}
              </div>
            </>
          )}

          {kind === "idea" && idea && <IdeaBody s={idea} />}
        </div>
      </aside>
    </>
  );
}

function MetricsBlock() {
  return (
    <div className="border-b border-[#EFE6D6] px-[18px] py-[16px] md:px-[28px] md:py-[18px]">
      <div className="mb-[12px] text-[11px] font-bold uppercase tracking-[.03em] text-faint md:mb-[13px]">О метриках</div>
      <div className="flex flex-col gap-[13px]">
        <div className="flex gap-[11px]">
          <span className="mt-[3px] h-[12px] w-[12px] flex-none rounded-[3px] bg-clay" />
          <div>
            <div className="mb-[3px] text-[13.5px] font-bold text-ink">Релевантность</div>
            <div className="text-[12.5px] leading-[1.5] text-prose">
              Насколько продукт стартапа близок к задаче этого агента — то есть к тому, что строим мы. Шкала 0–10: чем выше,
              тем сильнее пересечение с нашим направлением.
            </div>
          </div>
        </div>
        <div className="flex gap-[11px]">
          <span className="mt-[3px] h-[12px] w-[12px] flex-none rounded-[3px] bg-teal" />
          <div>
            <div className="mb-[3px] text-[13.5px] font-bold text-ink">Соответствие ПМО 2.0</div>
            <div className="text-[12.5px] leading-[1.5] text-prose">
              Насколько решение опирается на средства персонализированной модели образования: учебные материалы, совместную
              деятельность и общение, геймификацию и визуализацию, обратную связь и персонализированную траекторию. Шкала
              0–10: чем выше, тем зрелее продукт с точки зрения ПМО.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StartupCard({ s }: { s: Startup }) {
  return (
    <div className="rounded-[14px] border border-border-warm bg-white px-[15px] py-[14px] md:rounded-[15px] md:px-[18px] md:py-[17px]">
      <div className="flex items-start justify-between gap-[12px] md:gap-[16px]">
        <div className="min-w-0">
          <div className="text-[15.5px] font-bold leading-[1.2] tracking-[-.01em] md:text-[16px]">{s.name}</div>
          <div className="mt-[4px] flex flex-wrap items-center gap-[8px] md:mt-[6px]">
            <span className="text-[11.5px] font-semibold text-faint md:text-[12px]">{metaLine(s)}</span>
            {s.sectors.slice(0, 2).map((t) => (
              <span key={t} className="hidden rounded-[7px] border border-[#EBE0CE] bg-[#F4EEE2] px-[8px] py-[2px] text-[11px] font-semibold text-[#7A6E5B] md:inline">
                {t}
              </span>
            ))}
          </div>
        </div>
        <div className="flex flex-none items-start gap-[14px] md:gap-[18px]">
          <ScoreCell value={s.relevance} label="релевантность" color="#C2603C" sub={SCORE_LABEL.rel} />
          <ScoreCell value={s.pmoScore} label="ПМО" color="#3F8A78" sub={SCORE_LABEL.pmo} />
        </div>
      </div>
      {/* sector chips (mobile, under the row) */}
      {s.sectors.length > 0 && (
        <div className="mt-[10px] flex flex-wrap gap-[5px] md:hidden">
          {s.sectors.slice(0, 2).map((t) => (
            <span key={t} className="rounded-[6px] border border-[#EBE0CE] bg-[#F4EEE2] px-[7px] py-[3px] text-[10.5px] font-semibold text-[#7A6E5B]">
              {t}
            </span>
          ))}
        </div>
      )}
      {s.description && <div className="mt-[11px] text-[12.5px] leading-[1.5] text-[#5C5345] md:text-[13px]">{s.description}</div>}
      {s.rationale && <AiComment text={s.rationale} />}
    </div>
  );
}

function ScoreCell({ value, label, color, sub }: { value: number; label: string; color: string; sub: string }) {
  return (
    <div className="flex flex-col items-end">
      <span className="text-[21px] leading-none [font-variant-numeric:tabular-nums] md:text-[23px]" style={{ fontFamily: FONT_SERIF, color }}>
        {fmt1(value)}
      </span>
      <span className="mt-[2px] text-[9px] font-bold uppercase tracking-[.04em] md:mt-[3px] md:text-[9.5px]" style={{ color: sub }}>
        {label}
      </span>
    </div>
  );
}

function IdeaBody({ s }: { s: Startup }) {
  const data = [
    { label: "Основан", value: s.foundedYear ?? "—" },
    { label: "Стадия", value: s.stage || "—" },
    { label: "Фонд", value: s.fund || "—" },
    { label: "Инвестиция", value: s.investedYear ?? "—" },
  ];
  return (
    <div className="px-[18px] pb-[34px] pt-[16px] md:px-[28px] md:pt-[22px]">
      <SectionLabel>Оценки</SectionLabel>
      <div className="mb-[26px] grid grid-cols-2 gap-[14px]">
        <BigScore value={s.relevance} label="Релевантность" color="#C2603C" sub="#C9A98C" />
        <BigScore value={s.pmoScore} label="Соответствие ПМО 2.0" color="#3F8A78" sub="#9DBAAE" />
      </div>

      <SectionLabel>Данные</SectionLabel>
      <div className="mb-[26px] grid grid-cols-2 gap-px overflow-hidden rounded-[14px] border border-border-warm bg-border-warm">
        {data.map((d) => (
          <div key={d.label} className="bg-white px-[17px] py-[14px]">
            <div className="mb-[5px] text-[10.5px] font-bold uppercase tracking-[.04em] text-faint">{d.label}</div>
            <div className="text-[16px] font-bold text-ink [font-variant-numeric:tabular-nums]">{d.value}</div>
          </div>
        ))}
      </div>

      {s.groupRationale && (
        <div className="rounded-[13px] border border-[#F0DDC8] bg-white px-[16px] py-[14px]">
          <div className="mb-[7px] flex items-center gap-[6px] text-[10.5px] font-bold uppercase tracking-[.04em] text-clay">✦ Комментарий ИИ</div>
          <div className="text-[13px] leading-[1.55] text-prose">{s.groupRationale}</div>
        </div>
      )}
    </div>
  );
}

function BigScore({ value, label, color, sub }: { value: number; label: string; color: string; sub: string }) {
  return (
    <div className="rounded-[15px] border border-border-warm bg-white px-[19px] py-[17px]">
      <div className="flex items-baseline gap-[5px]">
        <span className="text-[40px] leading-none [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF, color }}>
          {fmt1(value)}
        </span>
        <span className="text-[15px] font-semibold" style={{ color: sub }}>
          / 10
        </span>
      </div>
      <div className="mt-[9px] text-[11px] font-bold uppercase tracking-[.04em] text-faint">{label}</div>
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <div className="mb-[13px] text-[10.5px] font-bold uppercase tracking-[.05em] text-faint">{children}</div>;
}

function AiComment({ text }: { text: string }) {
  return (
    <div className="mt-[12px] rounded-[11px] border border-[#F0E2D2] bg-[#FBF4EC] px-[13px] py-[11px]">
      <div className="mb-[6px] flex items-center gap-[6px] text-[10.5px] font-bold uppercase tracking-[.04em] text-clay">✦ Комментарий ИИ</div>
      <div className="text-[12.5px] leading-[1.5] text-prose">{text}</div>
    </div>
  );
}
