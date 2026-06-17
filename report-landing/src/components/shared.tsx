import type { CSSProperties } from "react";
import type { Startup } from "../types";
import { C, barW } from "../theme";

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

/** Thin labelled progress bar. `value` is on the 0–10 scale. */
export function Bar({
  value,
  fill,
  label,
  labelColor,
  caption,
}: {
  value: number;
  fill: string;
  label: string;
  labelColor: string;
  caption: string;
}) {
  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 11.5,
          fontWeight: 600,
          color: C.muted,
          marginBottom: 4,
        }}
      >
        <span>{caption}</span>
        <span style={{ color: labelColor, fontVariantNumeric: "tabular-nums" }}>{label}</span>
      </div>
      <div style={{ height: 6, borderRadius: 99, background: C.track, overflow: "hidden" }}>
        <div style={{ height: "100%", borderRadius: 99, background: fill, width: barW(value) }} />
      </div>
    </div>
  );
}

export const pill: CSSProperties = {
  fontSize: 12,
  fontWeight: 600,
  color: C.muted,
  background: "#fff",
  border: `1px solid ${C.border}`,
  borderRadius: 99,
  padding: "6px 12px",
};
