import type { AgentStatus } from "./types";

/** Warm-paper palette ported verbatim from the Claude Design mockup. */
export const C = {
  paper: "#F4EEE4",
  card: "#FBF8F2",
  cardAlt: "#F7F1E7",
  border: "#E7DECF",
  borderWarm: "#EBE2D2",
  ink: "#211C16",
  inkSoft: "#5C5345",
  muted: "#837A6C",
  faint: "#A9997F",
  track: "#EDE3D3",
  clay: "#C2603C", // relevance accent
  clayDeep: "#A6431F",
  teal: "#3F8A78", // pmo accent
} as const;

export const FONT_SERIF = "'Newsreader',serif";
export const FONT_SANS = "'Hanken Grotesk',system-ui,sans-serif";

export interface StatusMeta {
  label: string;
  color: string;
  bg: string;
}

/**
 * Real research data only has two agent statuses (no prod/idea tiers):
 *   «Протестировать» — agent built & ready to test  → green
 *   «В разработке»   — still under construction      → amber
 */
export function statusMeta(s: AgentStatus | string): StatusMeta {
  if (s === "Протестировать") return { label: "Протестировать", color: "#3F7D55", bg: "#E7F0E8" };
  if (s === "В разработке") return { label: "В разработке", color: "#A9781F", bg: "#F4EAD4" };
  return { label: s || "—", color: "#8A7461", bg: "#EEE6DB" };
}

/** Metrics live on a 0–10 scale; bars want a 0–100% width. */
export const barW = (v: number): string => `${Math.max(0, Math.min(100, v * 10))}%`;

const ruFmt = new Intl.NumberFormat("ru-RU");
export const fmtInt = (n: number): string => ruFmt.format(Math.round(n));

/** One decimal, trailing «.0» trimmed (8 → "8", 6.4 → "6,4"). */
export function fmt1(n: number): string {
  const r = Math.round(n * 10) / 10;
  return Number.isInteger(r) ? String(r) : r.toLocaleString("ru-RU", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}
