import type { Startup } from "../types";

/** "Fund · Stage · Year" line shown under every startup name. */
export function metaLine(s: Startup): string {
  return [s.fund, s.stage || "—", s.foundedYear ?? "—"].join(" · ");
}

export function StatusBadge({ label, color, bg, small }: { label: string; color: string; bg: string; small?: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-[6px] font-bold rounded-full whitespace-nowrap ${
        small ? "text-[11.5px] px-[9px] py-[4px]" : "text-[12px] px-[10px] py-[4px]"
      }`}
      style={{ background: bg, color }}
    >
      <span className="w-[6px] h-[6px] rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}

export function LegendItem({ color, text, square }: { color: string; text: string; square?: boolean }) {
  return (
    <span className="inline-flex items-center gap-[6px]">
      <span className={`w-[9px] h-[9px] ${square ? "rounded-[2px]" : "rounded-full"}`} style={{ background: color }} />
      {text}
    </span>
  );
}

