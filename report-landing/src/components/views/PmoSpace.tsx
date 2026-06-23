import type { AgentGroup } from "../../types";
import { FONT_SERIF, fmtInt, statusMeta } from "../../theme";
import type { Section } from "../../lib/report";

/** Пространство ПМО — agent cards grouped into the 5 средства. */
export default function PmoSpace({
  sections,
  onOpen,
  noResults,
}: {
  sections: Section<AgentGroup>[];
  onOpen: (id: number) => void;
  noResults: boolean;
}) {
  if (noResults) {
    return (
      <div className="px-[20px] py-[48px] text-center text-[14px] font-medium text-faint md:py-[60px]">
        Нет агентов под текущие фильтры. Сбросьте релевантность или статус.
      </div>
    );
  }

  return (
    <div className="animate-viewIn flex flex-col gap-[30px] md:gap-[40px]">
      {sections.map((g) => (
        <section key={g.name} data-group={`pmo::${g.name}`} className="scroll-mt-[140px]">
          <header className="mb-[13px] md:mb-[18px]">
            <div className="flex items-center gap-[11px] md:gap-[16px]">
              <span className="flex-none text-[15px] leading-none text-clay [font-variant-numeric:tabular-nums] md:text-[16px]" style={{ fontFamily: FONT_SERIF }}>
                {g.idx}
              </span>
              <h3 className="m-0 flex-none text-[15.5px] font-bold leading-[1.2] tracking-[-.01em] text-ink md:whitespace-nowrap md:text-[17px]">
                {g.name}
              </h3>
              <span className="hidden flex-none text-[12px] font-semibold text-faint [font-variant-numeric:tabular-nums] md:inline">
                {g.count} агентов
              </span>
              <span className="hidden h-px min-w-[24px] flex-1 bg-border-warm md:block" />
            </div>
            <div className="mt-[5px] text-[11.5px] font-semibold text-faint [font-variant-numeric:tabular-nums] md:hidden">
              {g.count} агентов
            </div>
          </header>

          <div className="grid grid-cols-1 gap-[11px] md:gap-[14px] md:[grid-template-columns:repeat(auto-fill,minmax(340px,1fr))]">
            {g.items.map((a) => (
              <AgentCard key={a.id} agent={a} onOpen={onOpen} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function AgentCard({ agent, onOpen }: { agent: AgentGroup; onOpen: (id: number) => void }) {
  const sm = statusMeta(agent.status);
  const empty = agent.count === 0;
  return (
    <button
      onClick={() => onOpen(agent.id)}
      className="flex min-h-0 cursor-pointer flex-col gap-[12px] rounded-[16px] border border-border-warm bg-card p-[16px] pb-[14px] text-left transition-all duration-150 md:min-h-[196px] md:gap-[14px] md:rounded-[18px] md:p-[22px] md:pb-[18px] md:hover:-translate-y-[2px] md:hover:border-[#D9C3B0] md:hover:[box-shadow:0_10px_26px_-14px_rgba(120,70,40,.28)]"
      style={{ borderColor: empty ? "#E2A78F" : undefined }}
    >
      <span className="inline-flex items-center gap-[7px] text-[11px] font-bold uppercase tracking-[.03em] md:text-[11.5px]" style={{ color: sm.color }}>
        <span className="h-[7px] w-[7px] flex-none rounded-full" style={{ background: sm.color }} />
        {sm.label}
      </span>
      <div className="flex-1 text-[19px] font-bold leading-[1.2] tracking-[-.015em] md:text-[23px]">{agent.name}</div>
      <div className="flex items-end justify-between gap-[8px] border-t border-[#EFE6D6] pt-[13px] md:pt-[14px]">
        <div className="flex items-baseline gap-[7px] md:gap-[8px]">
          <span className="text-[27px] leading-none tracking-[-.02em] text-ink [font-variant-numeric:tabular-nums] md:text-[32px]" style={{ fontFamily: FONT_SERIF }}>
            {fmtInt(agent.count)}
          </span>
          <span className="text-[12px] font-medium text-muted md:text-[12.5px]">стартапов</span>
        </div>
        <span className="text-[12.5px] font-bold text-clay">Открыть →</span>
      </div>
    </button>
  );
}
