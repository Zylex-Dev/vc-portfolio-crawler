import { useEffect, useMemo, useState } from "react";
import reportData from "./data/report.json";
import type { Agent, AgentGroup, Report, Startup } from "./types";
import { enrich } from "./lib/report";
import { C, FONT_SERIF, barW, fmt1, fmtInt, statusMeta } from "./theme";
import { StatusBadge, metaLine } from "./components/shared";
import Drawer, { type DrawerSelection, type DsortKey } from "./components/Drawer";
import AgentModal from "./components/AgentModal";

const report = reportData as Report;

type View = "grid" | "compact" | "map";
type SortKey = "count" | "relevance" | "pmo" | "name" | "status";

const VIEW_MODES: { v: View; label: string }[] = [
  { v: "grid", label: "Сетка" },
  { v: "compact", label: "Список" },
  { v: "map", label: "Карта групп" },
];

const STATUS_CHIPS: { v: string; label: string; dot: string }[] = [
  { v: "all", label: "Все", dot: "transparent" },
  { v: "Протестировать", label: "В проде", dot: "#3F7D55" },
  { v: "В разработке", label: "В разработке", dot: "#A9781F" },
];

export default function App() {
  const data = useMemo(() => enrich(report), []);
  const { meta, agents, maxCount, unmatched } = data;

  const [view, setView] = useState<View>("grid");
  const [sort, setSort] = useState<SortKey>("count");
  const [dir, setDir] = useState<"asc" | "desc">("desc");
  const [status, setStatus] = useState("all");
  const [minRel, setMinRel] = useState(0);
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<number | "unmatched" | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [dsort, setDsort] = useState<DsortKey>("relevance");
  const [infoAgent, setInfoAgent] = useState<Agent | null>(null);

  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      // The modal handles its own Escape; don't close the drawer underneath it.
      if (e.key === "Escape" && !infoAgent) setDrawerOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [infoAgent]);

  const openAgent = (id: number) => {
    setSelected(id);
    setDsort("relevance");
    setDrawerOpen(true);
  };
  const openUnmatched = () => {
    setSelected("unmatched");
    setDsort("pmo");
    setDrawerOpen(true);
  };

  const shown = useMemo(() => {
    const needle = q.trim().toLowerCase();
    let list = agents.filter((a) => {
      if (status !== "all" && a.status !== status) return false;
      if (needle && !(a.name.toLowerCase().includes(needle) || a.category.toLowerCase().includes(needle))) return false;
      return true;
    });
    // Relevance threshold no longer removes agent cards — it narrows each group
    // down to startups whose own relevance clears the bar (count reflects this).
    if (minRel > 0) {
      list = list.map((a) => {
        const group = a.group.filter((s) => s.relevance >= minRel);
        return { ...a, group, count: group.length };
      });
    }
    const d = dir === "asc" ? 1 : -1;
    const keyFns: Record<SortKey, (a: AgentGroup) => number | string> = {
      count: (a) => a.count,
      relevance: (a) => a.avgRel,
      pmo: (a) => a.avgPmo,
      name: (a) => a.name,
      status: (a) => a.status,
    };
    const f = keyFns[sort];
    return [...list].sort((x, y) => {
      const xa = f(x);
      const ya = f(y);
      if (typeof xa === "string" && typeof ya === "string") return xa.localeCompare(ya, "ru") * d;
      return ((xa as number) - (ya as number)) * d;
    });
  }, [agents, status, minRel, q, sort, dir]);

  const selection: DrawerSelection | null = useMemo(() => {
    if (selected === null) return null;
    if (selected === "unmatched") {
      return {
        kind: "unmatched",
        name: "Новые идеи",
        category: "Вне покрытия 44 агентов",
        status: { label: "Инсайт", color: C.clayDeep, bg: "#F2E0D4" },
        sredstvo: "—",
        description:
          "Стартапы, не совпавшие ни с одним агентом ПМО — источник новых продуктовых гипотез для пайплайна.",
        count: unmatched.count,
        avgRel: unmatched.avgRel,
        avgPmo: unmatched.avgPmo,
        sub: unmatched.sub,
        group: unmatched.group,
      };
    }
    const a = agents.find((x) => x.id === selected);
    if (!a) return null;
    const sm = statusMeta(a.status);
    return {
      kind: "agent",
      name: a.name,
      category: a.category,
      status: sm,
      sredstvo: a.sredstvo,
      description: a.role,
      count: a.count,
      avgRel: a.avgRel,
      avgPmo: a.avgPmo,
      sub: a.sub,
      group: a.group,
      agent: a,
    };
  }, [selected, agents, unmatched]);

  const heroStats = [
    { v: fmtInt(meta.totalCollected), l: "стартапов собрано", color: C.ink },
    { v: fmtInt(meta.totalStartups), l: "EdTech отфильтровано", color: C.ink },
    { v: fmtInt(meta.totalAgents), l: "ИИ-агентов ПМО", color: C.ink },
    { v: fmtInt(meta.matched), l: "сматчено с агентами", color: C.teal },
    { v: fmtInt(meta.unmatched), l: "новых идей вне покрытия", color: C.clay },
    { v: fmtInt(meta.totalFunds), l: "венчурных фондов", color: C.ink },
  ];

  return (
    <div style={{ background: C.paper, minHeight: "100vh" }}>
      {/* TOP BAR */}
      <header
        style={{
          position: "sticky",
          top: 0,
          zIndex: 50,
          background: "rgba(244,238,228,.86)",
          backdropFilter: "blur(12px)",
          borderBottom: `1px solid ${C.border}`,
        }}
      >
        <div style={{ maxWidth: 1240, margin: "0 auto", padding: "15px 28px", display: "flex", alignItems: "center", justifyContent: "center", gap: 13 }}>
          <div style={{ width: 34, height: 34, borderRadius: 10, background: C.clay, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 800, fontSize: 18 }}>
            П
          </div>
          <div style={{ fontWeight: 700, fontSize: 21, letterSpacing: "-.015em" }}>ПМО - Карта рынка агентов</div>
        </div>
      </header>

      {/* HERO */}
      <section style={{ position: "relative", overflow: "hidden", borderBottom: `1px solid ${C.border}` }}>
        <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(#D9CDB6 1.1px,transparent 1.1px)", backgroundSize: "24px 24px", opacity: 0.5 }} />
        <div style={{ position: "absolute", top: -160, right: -120, width: 520, height: 520, borderRadius: "50%", background: "radial-gradient(circle,rgba(194,96,60,.20),transparent 65%)" }} />
        <div style={{ position: "absolute", bottom: -200, left: -100, width: 480, height: 480, borderRadius: "50%", background: "radial-gradient(circle,rgba(63,138,120,.14),transparent 65%)" }} />
        <div style={{ position: "relative", maxWidth: 1240, margin: "0 auto", padding: "64px 28px 40px", animation: "fadeUp .5s both" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "#fff", border: `1px solid ${C.border}`, borderRadius: 99, padding: "6px 14px", fontSize: 12.5, fontWeight: 600, color: "#9A6A4A", marginBottom: 24 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: C.clay }} />
            Исследование венчурных портфелей 2026
          </div>
          <h1 style={{ fontFamily: FONT_SERIF, fontWeight: 400, fontSize: 54, lineHeight: 1.04, letterSpacing: "-.015em", margin: "0 0 18px" }}>
            Лучшие мировые практики EdTech&nbsp;стартапов для воплощения ПМО на практике
          </h1>
          <p style={{ fontSize: 18, lineHeight: 1.55, color: C.inkSoft, maxWidth: "62ch", margin: "0 0 40px", fontWeight: 450 }}>
            Мы собрали <b style={{ color: C.ink, fontWeight: 700 }}>{fmtInt(meta.totalCollected)}</b> стартапов из портфелей крупных венчурных фондов,
            отфильтровали <b style={{ color: C.ink, fontWeight: 700 }}>{fmtInt(meta.totalStartups)}</b> EdTech-решений и сопоставили каждое
            с <b style={{ color: C.ink, fontWeight: 700 }}>{meta.totalAgents}</b> ИИ-агентами персонализированной модели образования.
            Ниже — интерактивная карта совпадений и зона новых идей.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 1, background: C.border, border: `1px solid ${C.border}`, borderRadius: 18, overflow: "hidden" }}>
            {heroStats.map((s) => (
              <div key={s.l} style={{ background: C.card, padding: "22px 22px 20px" }}>
                <div style={{ fontFamily: FONT_SERIF, fontSize: 34, lineHeight: 1, letterSpacing: "-.02em", fontVariantNumeric: "tabular-nums", color: s.color }}>{s.v}</div>
                <div style={{ fontSize: 12.5, color: "#837A6C", marginTop: 8, fontWeight: 500, lineHeight: 1.35 }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CONTROLS */}
      <div style={{ position: "sticky", top: 53, zIndex: 40, background: "rgba(244,238,228,.92)", backdropFilter: "blur(12px)", borderBottom: `1px solid ${C.border}` }}>
        <div style={{ maxWidth: 1240, margin: "0 auto", padding: "14px 28px", display: "flex", flexWrap: "wrap", alignItems: "center", gap: 14 }}>
          <div style={{ display: "flex", gap: 4, background: "#EBE2D2", border: "1px solid #E1D6C2", borderRadius: 99, padding: 4 }}>
            {VIEW_MODES.map((m) => {
              const on = view === m.v;
              return (
                <button
                  key={m.v}
                  onClick={() => setView(m.v)}
                  style={{ border: "none", cursor: "pointer", fontWeight: 600, fontSize: 13, padding: "7px 15px", borderRadius: 99, transition: "all .15s", background: on ? C.ink : "transparent", color: on ? "#fff" : C.muted }}
                >
                  {m.label}
                </button>
              );
            })}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            {STATUS_CHIPS.map((c) => {
              const on = status === c.v;
              return (
                <button
                  key={c.v}
                  onClick={() => setStatus(c.v)}
                  style={{ display: "inline-flex", alignItems: "center", gap: 7, border: `1px solid ${on ? C.ink : C.border}`, cursor: "pointer", fontWeight: 600, fontSize: 12.5, padding: "7px 13px", borderRadius: 99, transition: "all .15s", background: on ? C.ink : "#fff", color: on ? "#fff" : "#4A4339" }}
                >
                  <span style={{ width: 7, height: 7, borderRadius: "50%", background: on ? (c.v === "all" ? "#fff" : c.dot) : c.dot }} />
                  {c.label}
                </button>
              );
            })}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 11, background: "#fff", border: `1px solid ${C.border}`, borderRadius: 99, padding: "7px 15px" }}>
            <span style={{ fontSize: 12.5, fontWeight: 600, color: C.muted, whiteSpace: "nowrap" }}>Релевантность ≥</span>
            <input type="range" min={0} max={10} step={1} value={minRel} onChange={(e) => setMinRel(Number(e.target.value))} style={{ width: 108 }} aria-label="Минимальная релевантность" />
            <span style={{ fontSize: 12.5, fontWeight: 700, color: C.clay, fontVariantNumeric: "tabular-nums", minWidth: 34 }}>{minRel === 0 ? "любая" : minRel}</span>
          </div>

          <div style={{ flex: 1 }} />

          <div style={{ position: "relative", display: "flex", alignItems: "center", background: "#fff", border: `1px solid ${C.border}`, borderRadius: 99, padding: "0 6px 0 14px" }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#A9997F" strokeWidth="2.2">
              <circle cx="11" cy="11" r="7" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input type="text" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Поиск агента…" aria-label="Поиск агента" style={{ border: "none", outline: "none", background: "transparent", fontSize: 13, padding: "8px 8px", width: 140, color: C.ink }} />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)} aria-label="Сортировка" style={{ border: `1px solid ${C.border}`, background: "#fff", borderRadius: 99, padding: "8px 13px", fontSize: 12.5, fontWeight: 600, color: "#4A4339", cursor: "pointer", outline: "none" }}>
              <option value="count">По размеру группы</option>
              <option value="relevance">По релевантности</option>
              <option value="pmo">По соответствию ПМО 2.0</option>
              <option value="name">По названию</option>
              <option value="status">По статусу</option>
            </select>
            <button onClick={() => setDir(dir === "asc" ? "desc" : "asc")} title="Направление" aria-label="Направление сортировки" style={{ border: `1px solid ${C.border}`, background: "#fff", borderRadius: "50%", width: 34, height: 34, cursor: "pointer", fontSize: 14, color: "#4A4339", display: "flex", alignItems: "center", justifyContent: "center" }}>
              {dir === "asc" ? "↑" : "↓"}
            </button>
          </div>
        </div>
      </div>

      {/* MAIN */}
      <main style={{ maxWidth: 1240, margin: "0 auto", padding: "30px 28px 70px" }}>
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 16, marginBottom: 20 }}>
          <h2 style={{ fontFamily: FONT_SERIF, fontWeight: 400, fontSize: 24, letterSpacing: "-.01em", margin: 0 }}><span style={{ fontWeight: 700 }}>{meta.totalAgents}</span> Агента персонализированной модели образования</h2>
          <div style={{ fontSize: 13, color: C.muted, fontWeight: 500 }}>
            Показано <b style={{ color: C.ink }}>{shown.length}</b> из {meta.totalAgents}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 22, fontSize: 12, color: "#9A8F7C", fontWeight: 600, flexWrap: "wrap" }}>
          <LegendItem square color={C.clay} text="релевантность" />
          <LegendItem square color={C.teal} text="соответствие ПМО 2.0" />
          <LegendItem color="#3F7D55" text="в проде" />
          <LegendItem color="#A9781F" text="в разработке" />
        </div>

        {shown.length === 0 ? (
          <div style={{ textAlign: "center", padding: "60px 20px", color: C.faint, fontWeight: 500 }}>
            Нет агентов под текущие фильтры
          </div>
        ) : view === "grid" ? (
          <GridView agents={shown} onOpen={openAgent} />
        ) : view === "compact" ? (
          <CompactView agents={shown} maxCount={maxCount} onOpen={openAgent} />
        ) : (
          <MapView agents={shown} maxCount={maxCount} onOpen={openAgent} />
        )}

        <UnmatchedSection unmatched={unmatched} onOpen={openUnmatched} />
      </main>

      <Drawer open={drawerOpen} selection={selection} minRel={minRel} dsort={dsort} onDsort={setDsort} onClose={() => setDrawerOpen(false)} onOpenInfo={setInfoAgent} />
      <AgentModal agent={infoAgent} onClose={() => setInfoAgent(null)} />
    </div>
  );
}

function LegendItem({ color, text, square }: { color: string; text: string; square?: boolean }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={{ width: 9, height: 9, borderRadius: square ? 2 : "50%", background: color }} />
      {text}
    </span>
  );
}

/* ---------- GRID ---------- */
function GridView({ agents, onOpen }: { agents: AgentGroup[]; onOpen: (id: number) => void }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(286px,1fr))", gap: 14 }}>
      {agents.map((a) => {
        const sm = statusMeta(a.status);
        return (
          <button key={a.id} className="agent-card" onClick={() => onOpen(a.id)} style={{ textAlign: "left", cursor: "pointer", background: C.card, border: `1px solid ${C.borderWarm}`, borderRadius: 18, padding: "18px 18px 16px", display: "flex", flexDirection: "column", gap: 14 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".02em", textTransform: "uppercase", color: C.faint }}>{a.category}</span>
              <StatusBadge label={sm.label} color={sm.color} bg={sm.bg} small />
            </div>
            <div style={{ fontSize: 19, fontWeight: 700, letterSpacing: "-.01em", lineHeight: 1.25, color: C.ink, minHeight: "3.75em", display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }} title={a.name}>{a.name}</div>
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 8, borderTop: "1px solid #EFE6D6", paddingTop: 11, marginTop: "auto" }}>
              <span style={{ display: "flex", alignItems: "baseline", gap: 7 }}>
                <span style={{ fontFamily: FONT_SERIF, fontSize: 32, lineHeight: 1, letterSpacing: "-.02em", fontVariantNumeric: "tabular-nums", color: C.ink }}>{fmtInt(a.count)}</span>
                <span style={{ fontSize: 12.5, color: C.muted, fontWeight: 500 }}>стартапов</span>
              </span>
              <span style={{ fontSize: 12.5, fontWeight: 700, color: C.clay }}>Открыть →</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}

/* ---------- COMPACT ---------- */
function CompactView({ agents, maxCount, onOpen }: { agents: AgentGroup[]; maxCount: number; onOpen: (id: number) => void }) {
  const cols = "1fr 120px 116px 116px 40px";
  return (
    <div style={{ background: C.card, border: `1px solid ${C.borderWarm}`, borderRadius: 18, overflow: "hidden" }}>
      <div style={{ display: "grid", gridTemplateColumns: cols, gap: 14, padding: "13px 20px", borderBottom: "1px solid #EFE6D6", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".03em", color: C.faint }}>
        <span>Агент</span>
        <span>Группа</span>
        <span>Релевантность</span>
        <span>Соответствие ПМО 2.0</span>
        <span />
      </div>
      {agents.map((a) => {
        const sm = statusMeta(a.status);
        return (
          <button key={a.id} className="agent-row" onClick={() => onOpen(a.id)} style={{ width: "100%", textAlign: "left", cursor: "pointer", background: "transparent", border: "none", borderBottom: "1px solid #F0E8D9", display: "grid", gridTemplateColumns: cols, gap: 14, alignItems: "center", padding: "13px 20px" }}>
            <span style={{ display: "flex", alignItems: "center", gap: 11, minWidth: 0 }}>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: sm.color, flex: "none" }} />
              <span style={{ minWidth: 0 }}>
                <span style={{ display: "block", fontSize: 14.5, fontWeight: 700, letterSpacing: "-.01em", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{a.name}</span>
                <span style={{ display: "block", fontSize: 11.5, color: C.faint, fontWeight: 500 }}>{a.category}</span>
              </span>
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: 9 }}>
              <span style={{ fontSize: 15, fontWeight: 700, fontVariantNumeric: "tabular-nums", minWidth: 30 }}>{fmtInt(a.count)}</span>
              <span style={{ flex: 1, height: 6, borderRadius: 99, background: C.track, overflow: "hidden" }}>
                <span style={{ display: "block", height: "100%", background: "#C9A98C", width: `${Math.round((a.count / maxCount) * 100)}%` }} />
              </span>
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ flex: 1, height: 6, borderRadius: 99, background: C.track, overflow: "hidden" }}>
                <span style={{ display: "block", height: "100%", background: C.clay, width: barW(a.avgRel) }} />
              </span>
              <span style={{ fontSize: 12.5, fontWeight: 700, color: C.clay, fontVariantNumeric: "tabular-nums" }}>{fmt1(a.avgRel)}</span>
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ flex: 1, height: 6, borderRadius: 99, background: C.track, overflow: "hidden" }}>
                <span style={{ display: "block", height: "100%", background: C.teal, width: barW(a.avgPmo) }} />
              </span>
              <span style={{ fontSize: 12.5, fontWeight: 700, color: C.teal, fontVariantNumeric: "tabular-nums" }}>{fmt1(a.avgPmo)}</span>
            </span>
            <span style={{ color: C.clay, fontWeight: 700, fontSize: 15, textAlign: "right" }}>→</span>
          </button>
        );
      })}
    </div>
  );
}

/* ---------- MAP ---------- */
function MapView({ agents, maxCount, onOpen }: { agents: AgentGroup[]; maxCount: number; onOpen: (id: number) => void }) {
  return (
    <div style={{ background: C.card, border: `1px solid ${C.borderWarm}`, borderRadius: 18, padding: 22 }}>
      <p style={{ margin: "0 0 18px", fontSize: 13, color: C.muted, fontWeight: 500 }}>Размер плитки — число стартапов в группе. Цвет — стадия реализации агента.</p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "flex-end" }}>
        {agents.map((a) => {
          const sm = statusMeta(a.status);
          const size = Math.round(54 + Math.sqrt(a.count / maxCount) * 116);
          return (
            <button key={a.id} className="agent-tile" onClick={() => onOpen(a.id)} title={a.name} style={{ cursor: "pointer", border: `1px solid ${sm.color}`, background: sm.bg, color: sm.color, borderRadius: 13, padding: 10, display: "flex", flexDirection: "column", justifyContent: "space-between", overflow: "hidden", width: size, height: size }}>
              <span style={{ fontSize: 11, fontWeight: 700, lineHeight: 1.15, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}>{a.name}</span>
              <span style={{ fontFamily: FONT_SERIF, fontSize: 21, lineHeight: 1, fontVariantNumeric: "tabular-nums", alignSelf: "flex-end" }}>{fmtInt(a.count)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

/* ---------- UNMATCHED ---------- */
function UnmatchedSection({ unmatched, onOpen }: { unmatched: ReturnType<typeof enrich>["unmatched"]; onOpen: () => void }) {
  const samples: Startup[] = [...unmatched.group].sort((a, b) => b.pmoScore - a.pmoScore).slice(0, 4);
  return (
    <section style={{ marginTop: 46, position: "relative", overflow: "hidden", borderRadius: 24, border: "1px solid #E6CDB8", background: "linear-gradient(135deg,#FBEDE2,#F7F0E4)" }}>
      <div style={{ position: "absolute", top: -90, right: -60, width: 340, height: 340, borderRadius: "50%", background: "radial-gradient(circle,rgba(194,96,60,.16),transparent 65%)" }} />
      <div style={{ position: "relative", padding: "34px 32px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-end", justifyContent: "space-between", gap: 20, marginBottom: 26 }}>
          <div style={{ maxWidth: "54ch" }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "#fff", border: "1px solid #E6CDB8", borderRadius: 99, padding: "5px 13px", fontSize: 12, fontWeight: 700, color: C.clayDeep, marginBottom: 16 }}>
              <span style={{ width: 7, height: 7, borderRadius: "50%", background: C.clay }} />
              Зона новых идей
            </div>
            <h2 style={{ fontFamily: FONT_SERIF, fontWeight: 400, fontSize: 30, letterSpacing: "-.015em", margin: "0 0 10px", lineHeight: 1.1 }}>
              {fmtInt(unmatched.count)} стартапов вне покрытия 44 агентов
            </h2>
            <p style={{ margin: 0, fontSize: 15, lineHeight: 1.55, color: "#6B5E4D", fontWeight: 450 }}>
              Эти команды не совпали ни с одним нашим агентом — самый ценный срез исследования. Каждый из них — кандидат на новую продуктовую гипотезу для пайплайна ПМО.
            </p>
          </div>
          <button onClick={onOpen} style={{ cursor: "pointer", fontWeight: 700, fontSize: 14, color: "#fff", background: C.clay, border: "none", borderRadius: 99, padding: "13px 22px", whiteSpace: "nowrap", boxShadow: "0 8px 20px -8px rgba(194,96,60,.6)" }}>
            Смотреть все {fmtInt(unmatched.count)} →
          </button>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 22 }}>
          <div style={{ background: "#fff", border: "1px solid #EBDCC9", borderRadius: 13, padding: "13px 18px" }}>
            <div style={{ fontFamily: FONT_SERIF, fontSize: 25, lineHeight: 1, color: C.teal, fontVariantNumeric: "tabular-nums" }}>{fmt1(unmatched.avgPmo)}</div>
            <div style={{ fontSize: 11.5, color: "#9A8F7C", fontWeight: 600, marginTop: 5 }}>среднее соответствие ПМО 2.0</div>
          </div>
          {unmatched.topSectors.map((s) => (
            <div key={s} style={{ background: "#fff", border: "1px solid #EBDCC9", borderRadius: 13, padding: "13px 18px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: C.ink }}>{s}</div>
              <div style={{ fontSize: 11.5, color: "#9A8F7C", fontWeight: 600, marginTop: 4 }}>частый сектор</div>
            </div>
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(250px,1fr))", gap: 12 }}>
          {samples.map((s) => (
            <div key={s.id} style={{ background: "#fff", border: "1px solid #EBDCC9", borderRadius: 15, padding: 16 }}>
              <div style={{ fontSize: 15.5, fontWeight: 700, letterSpacing: "-.01em" }}>{s.name}</div>
              <div style={{ fontSize: 12, color: C.faint, fontWeight: 600, margin: "7px 0 9px" }}>{metaLine(s)}</div>
              <div style={{ fontSize: 12.5, color: "#6B5E4D", lineHeight: 1.45 }}>{clampText(s.description, 160)}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function clampText(text: string, max: number): string {
  if (!text) return "";
  return text.length <= max ? text : text.slice(0, max).trimEnd() + "…";
}
