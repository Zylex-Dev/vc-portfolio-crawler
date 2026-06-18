import { useMemo } from "react";
import type { Agent, PmoSub, Startup } from "../types";
import { C, FONT_SERIF, fmt1 } from "../theme";
import { StatusBadge, metaLine } from "./shared";

export interface DrawerSelection {
  kind: "agent" | "unmatched";
  name: string;
  category: string;
  status: { label: string; color: string; bg: string };
  sredstvo: string;
  description: string;
  count: number;
  avgRel: number;
  avgPmo: number;
  sub: PmoSub;
  group: Startup[];
  agent?: Agent;
}

const DSORT = {
  relevance: (s: Startup) => s.relevance,
  pmo: (s: Startup) => s.pmoScore,
  year: (s: Startup) => s.foundedYear ?? 0,
  name: (s: Startup) => s.name,
} as const;

export type DsortKey = keyof typeof DSORT;

export default function Drawer({
  open,
  selection,
  minRel,
  dsort,
  onDsort,
  onClose,
  onOpenInfo,
}: {
  open: boolean;
  selection: DrawerSelection | null;
  minRel: number;
  dsort: DsortKey;
  onDsort: (v: DsortKey) => void;
  onClose: () => void;
  onOpenInfo: (agent: Agent) => void;
}) {
  const startups = useMemo(() => {
    if (!selection) return [];
    const f = DSORT[dsort] ?? DSORT.relevance;
    return [...selection.group]
      .filter((s) => s.relevance >= minRel)
      .sort((a, b) => {
        const xa = f(a);
        const ya = f(b);
        if (typeof xa === "string" && typeof ya === "string") return xa.localeCompare(ya, "ru");
        return (ya as number) - (xa as number);
      });
  }, [selection, dsort, minRel]);

  return (
    <>
      <div
        onClick={onClose}
        aria-hidden
        style={{
          position: "fixed",
          inset: 0,
          zIndex: 90,
          background: "rgba(40,28,18,.34)",
          backdropFilter: "blur(2px)",
          transition: "opacity .28s",
          opacity: open ? 1 : 0,
          pointerEvents: open ? "auto" : "none",
        }}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-label={selection?.name ?? "Группа"}
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          bottom: 0,
          zIndex: 91,
          width: "min(760px,94vw)",
          background: C.cardAlt,
          boxShadow: "-24px 0 60px -30px rgba(60,40,20,.5)",
          transition: "transform .32s cubic-bezier(.22,1,.36,1)",
          transform: open ? "translateX(0)" : "translateX(100%)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {selection && (
          <>
            {/* header */}
            <div style={{ padding: "22px 28px 18px", borderBottom: `1px solid ${C.border}`, background: C.card }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, marginBottom: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
                  <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".03em", color: C.faint }}>
                    {selection.category}
                  </span>
                  <StatusBadge label={selection.status.label} color={selection.status.color} bg={selection.status.bg} small />
                </div>
                <button
                  onClick={onClose}
                  aria-label="Закрыть"
                  style={{
                    cursor: "pointer",
                    border: `1px solid ${C.border}`,
                    background: "#fff",
                    borderRadius: "50%",
                    width: 34,
                    height: 34,
                    fontSize: 17,
                    color: C.muted,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  ✕
                </button>
              </div>
              <h2 style={{ fontFamily: FONT_SERIF, fontWeight: 400, fontSize: 30, letterSpacing: "-.015em", margin: "0 0 8px", lineHeight: 1.08 }}>
                {selection.kind === "agent" && selection.agent ? (
                  <button
                    className="agent-title-link"
                    onClick={() => onOpenInfo(selection.agent!)}
                    title="Открыть подробную информацию об агенте"
                    style={{ fontFamily: "inherit", fontSize: "inherit", fontWeight: "inherit", letterSpacing: "inherit", lineHeight: "inherit", color: C.ink }}
                  >
                    {selection.name}
                  </button>
                ) : (
                  selection.name
                )}
              </h2>
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.5, color: "#6B5E4D", maxWidth: "64ch" }}>{selection.description}</p>
              {selection.kind === "agent" && selection.agent?.resourceLink && (
                <a
                  href={selection.agent.resourceLink}
                  target="_blank"
                  rel="noreferrer"
                  style={{ display: "inline-block", marginTop: 12, fontSize: 12.5, fontWeight: 700, color: C.clay, textDecoration: "none" }}
                >
                  Открыть прототип агента →
                </a>
              )}
            </div>

            {/* how to read the metrics */}
            <div style={{ padding: "18px 28px", borderBottom: `1px solid ${C.border}` }}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".03em", color: C.faint, marginBottom: 12 }}>
                О метриках
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div style={{ display: "flex", gap: 11 }}>
                  <span style={{ width: 9, height: 9, borderRadius: 2, background: C.clay, marginTop: 5, flex: "none" }} />
                  <div>
                    <div style={{ fontSize: 13.5, fontWeight: 700, color: C.ink, marginBottom: 2 }}>Релевантность</div>
                    <div style={{ fontSize: 13, lineHeight: 1.5, color: "#6B5E4D" }}>
                      Насколько продукт стартапа близок к задаче этого агента — то есть к тому, что строим мы.
                      Шкала 0–10: чем выше, тем сильнее пересечение с нашим направлением.
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 11 }}>
                  <span style={{ width: 9, height: 9, borderRadius: 2, background: C.teal, marginTop: 5, flex: "none" }} />
                  <div>
                    <div style={{ fontSize: 13.5, fontWeight: 700, color: C.ink, marginBottom: 2 }}>Соответствие ПМО 2.0</div>
                    <div style={{ fontSize: 13, lineHeight: 1.5, color: "#6B5E4D" }}>
                      Насколько решение опирается на принципы персонализированной модели образования:
                      траекторию, материалы, коллаборацию, геймификацию и обратную связь.
                      Шкала 0–10: чем выше, тем зрелее продукт с точки зрения ПМО.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* list toolbar */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, padding: "14px 28px 10px" }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.muted }}>
                Стартапы группы · <b style={{ color: C.ink }}>{startups.length}</b>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <span style={{ fontSize: 12, color: C.faint, fontWeight: 600 }}>Сортировка</span>
                <select
                  value={dsort}
                  onChange={(e) => onDsort(e.target.value as DsortKey)}
                  style={{ border: `1px solid ${C.border}`, background: "#fff", borderRadius: 99, padding: "7px 12px", fontSize: 12.5, fontWeight: 600, color: "#4A4339", cursor: "pointer", outline: "none" }}
                >
                  <option value="relevance">релевантность</option>
                  <option value="pmo">соответствие ПМО 2.0</option>
                  <option value="year">год основания</option>
                  <option value="name">название</option>
                </select>
              </div>
            </div>

            {/* startup cards */}
            <div style={{ flex: 1, overflowY: "auto", padding: "6px 28px 32px" }}>
              {startups.map((s) => (
                <StartupCard key={s.id} s={s} />
              ))}
              {startups.length === 0 && (
                <div style={{ textAlign: "center", padding: "40px 20px", color: C.faint, fontWeight: 500 }}>
                  Нет данных по стартапам
                </div>
              )}
            </div>
          </>
        )}
      </aside>
    </>
  );
}

function StartupCard({ s }: { s: Startup }) {
  return (
    <div style={{ background: "#fff", border: `1px solid ${C.borderWarm}`, borderRadius: 15, padding: "16px 17px", marginBottom: 11 }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-.01em" }}>
            {s.website ? (
              <a className="startup-link" href={s.website} target="_blank" rel="noreferrer" style={{ color: C.ink, textDecoration: "none" }}>
                {s.name}
              </a>
            ) : (
              s.name
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
            <span style={{ fontSize: 12, color: C.faint, fontWeight: 600 }}>{metaLine(s)}</span>
            {s.sectors.map((t) => (
              <span key={t} style={{ fontSize: 11, fontWeight: 600, color: "#7A6E5B", background: "#F4EEE2", border: "1px solid #EBE0CE", borderRadius: 7, padding: "3px 8px" }}>
                {t}
              </span>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 18, flex: "none" }}>
          <ScoreBlock label="Релевантность" value={s.relevance} color={C.clay} />
          <ScoreBlock label="ПМО" value={s.pmoScore} color={C.teal} />
        </div>
      </div>

      {s.description && <div style={{ fontSize: 13, color: C.inkSoft, lineHeight: 1.5, marginTop: 11 }}>{clamp(s.description, 320)}</div>}
      {s.rationale && (
        <div style={{ fontSize: 12.5, color: "#9A8F7C", lineHeight: 1.5, fontStyle: "italic", borderLeft: "2px solid #E6CDB8", paddingLeft: 11, marginTop: 10 }}>
          {s.rationale}
        </div>
      )}
    </div>
  );
}

function ScoreBlock({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 2 }}>
      <span style={{ fontFamily: FONT_SERIF, fontSize: 23, lineHeight: 1, color, fontVariantNumeric: "tabular-nums" }}>{fmt1(value)}</span>
      <span style={{ fontSize: 9.5, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".03em", color, whiteSpace: "nowrap" }}>{label}</span>
    </div>
  );
}

function clamp(text: string, max: number): string {
  if (text.length <= max) return text;
  return text.slice(0, max).trimEnd() + "…";
}
