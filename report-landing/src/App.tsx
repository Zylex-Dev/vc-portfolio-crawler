import { useEffect, useMemo, useState } from "react";
import reportData from "./data/report.json";
import type { Agent, AgentGroup, Report } from "./types";
import { enrich } from "./lib/report";
import { C, FONT_SERIF, statusMeta } from "./theme";
import Drawer, { type DrawerSelection, type DsortKey } from "./components/Drawer";
import AgentModal from "./components/AgentModal";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Controls, { type View, type SortKey } from "./components/Controls";
import GridView from "./components/views/GridView";
import CompactView from "./components/views/CompactView";
import MapView from "./components/views/MapView";
import UnmatchedSection from "./components/UnmatchedSection";
import { LegendItem } from "./components/shared";

const report = reportData as Report;

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

  return (
    <div className="min-h-screen bg-paper">
      <Header />
      <Hero meta={meta} />
      <Controls view={view} setView={setView} status={status} setStatus={setStatus} minRel={minRel} setMinRel={setMinRel} q={q} setQ={setQ} sort={sort} setSort={setSort} dir={dir} setDir={setDir} />

      <main className="mx-auto max-w-[1240px] px-[28px] pb-[70px] pt-[30px]">
        <div className="mb-[20px] flex items-baseline justify-between gap-[16px]">
          <h2 className="m-0 text-[24px] font-normal tracking-[-.01em]" style={{ fontFamily: FONT_SERIF }}>
            <span className="font-bold">{meta.totalAgents}</span> Агента персонализированной модели образования
          </h2>
          <div className="text-[13px] font-medium text-muted">
            Показано <b className="text-ink">{shown.length}</b> из {meta.totalAgents}
          </div>
        </div>
        <div className="mb-[22px] flex flex-wrap items-center gap-[18px] text-[12px] font-semibold text-[#9A8F7C]">
          <LegendItem square color={C.clay} text="релевантность" />
          <LegendItem square color={C.teal} text="соответствие ПМО 2.0" />
          <LegendItem color="#3F7D55" text="в проде" />
          <LegendItem color="#A9781F" text="в разработке" />
        </div>

        {shown.length === 0 ? (
          <div className="px-[20px] py-[60px] text-center font-medium text-faint">
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

