import type { AgentGroup } from "../../types";
import { barW, fmt1, fmtInt, statusMeta } from "../../theme";

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
