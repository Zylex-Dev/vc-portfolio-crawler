import type { Startup } from "../types";

/** "Fund · Stage · Year" line shown under every startup name. */
export function metaLine(s: Startup): string {
  return [s.fund, s.stage || "—", s.foundedYear ?? "—"].join(" · ");
}

export function StatusBadge({
  label,
  color,
  bg,
  small,
}: {
  label: string;
  color: string;
  bg: string;
  small?: boolean;
}) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        fontSize: small ? 11.5 : 12,
        fontWeight: 700,
        padding: small ? "4px 9px" : "4px 10px",
        borderRadius: 99,
        background: bg,
        color,
        whiteSpace: "nowrap",
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: color }} />
      {label}
    </span>
  );
}

