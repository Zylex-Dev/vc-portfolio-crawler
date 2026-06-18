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
