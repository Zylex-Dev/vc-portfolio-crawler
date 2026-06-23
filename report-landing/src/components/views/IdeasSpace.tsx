import type { Startup } from "../../types";
import { FONT_SERIF, SCORE_LABEL, fmt1 } from "../../theme";
import type { Section } from "../../lib/report";

/** The accent label on a startup card: funding stage, else first sector. */
const ideaLabel = (s: Startup) => s.stage || s.sectors[0] || "—";

/** Пространство новых идей — startup cards grouped into the 7 niches. */
export default function IdeasSpace({
  sections,
  onOpen,
  noResults,
}: {
  sections: Section<Startup>[];
  onOpen: (id: number) => void;
  noResults: boolean;
}) {
  if (noResults) {
    return (
      <div className="px-[20px] py-[48px] text-center text-[14px] font-medium text-faint md:py-[60px]">
        Нет стартапов под выбранные фильтры.
      </div>
    );
  }

  return (
    <div className="animate-viewIn flex flex-col gap-[30px] md:gap-[40px]">
      {sections.map((g) => (
        <section key={g.name} data-group={`ideas::${g.name}`} className="scroll-mt-[140px]">
          <header className="mb-[13px] md:mb-[18px]">
            <div className="flex items-center gap-[11px] md:gap-[16px]">
              <span className="flex-none text-[15px] leading-none text-teal [font-variant-numeric:tabular-nums] md:text-[16px]" style={{ fontFamily: FONT_SERIF }}>
                {g.idx}
              </span>
              <h3 className="m-0 flex-none text-[15.5px] font-bold leading-[1.2] tracking-[-.01em] text-ink md:text-[17px]">
                {g.name}
              </h3>
              <span className="hidden flex-none text-[12px] font-semibold text-faint [font-variant-numeric:tabular-nums] md:inline">
                {g.count} стартапов
              </span>
              <span className="hidden h-px min-w-[24px] flex-1 bg-border-warm md:block" />
            </div>
            <div className="mt-[5px] text-[11.5px] font-semibold text-faint [font-variant-numeric:tabular-nums] md:hidden">
              {g.count} стартапов
            </div>
          </header>

          <div className="grid grid-cols-1 gap-[11px] md:gap-[14px] md:[grid-template-columns:repeat(auto-fill,minmax(320px,1fr))]">
            {g.items.map((s) => (
              <IdeaCard key={s.id} startup={s} onOpen={onOpen} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function IdeaCard({ startup: s, onOpen }: { startup: Startup; onOpen: (id: number) => void }) {
  return (
    <button
      onClick={() => onOpen(s.id)}
      className="flex min-h-0 cursor-pointer flex-col gap-[12px] rounded-[16px] border border-border-warm bg-card p-[16px] pb-[14px] text-left transition-all duration-150 md:min-h-[196px] md:gap-[14px] md:rounded-[18px] md:p-[22px] md:pb-[18px] md:hover:-translate-y-[2px] md:hover:border-[#B7D2C8] md:hover:[box-shadow:0_10px_26px_-14px_rgba(40,90,75,.26)]"
    >
      <span className="inline-flex items-center gap-[7px] text-[11px] font-bold uppercase tracking-[.03em] text-teal md:text-[11.5px]">
        <span className="h-[7px] w-[7px] flex-none rounded-full bg-teal" />
        {ideaLabel(s)}
      </span>
      <div className="flex-1 text-[19px] font-bold leading-[1.2] tracking-[-.015em] md:text-[23px]">{s.name}</div>
      <div className="flex items-end justify-between gap-[8px] border-t border-[#EFE6D6] pt-[13px] md:pt-[14px]">
        <div className="flex items-baseline gap-[14px]">
          <Score value={s.relevance} label="рел" color={SCORE_LABEL.rel} />
          <Score value={s.pmoScore} label="пмо" color={SCORE_LABEL.pmo} />
        </div>
        <span className="text-[12.5px] font-bold text-teal">Открыть →</span>
      </div>
    </button>
  );
}

function Score({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <span className="flex items-baseline gap-[5px]">
      <span className="text-[27px] leading-none tracking-[-.02em] text-ink [font-variant-numeric:tabular-nums] md:text-[32px]" style={{ fontFamily: FONT_SERIF }}>
        {fmt1(value)}
      </span>
      <span className="text-[10.5px] font-bold uppercase tracking-[.04em] md:text-[11px]" style={{ color }}>
        {label}
      </span>
    </span>
  );
}
