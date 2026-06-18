import type { AgentGroup } from "../../types";
import { FONT_SERIF, fmtInt, statusMeta } from "../../theme";
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
