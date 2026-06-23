import { useEffect, useMemo, useRef, useState } from "react";
import reportData from "./data/report.json";
import type { Agent, Report, Startup } from "./types";
import { enrich, groupAgents, groupIdeas } from "./lib/report";
import { buildPuzzle } from "./lib/puzzle";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Controls from "./components/Controls";
import MapView from "./components/views/MapView";
import PmoSpace from "./components/views/PmoSpace";
import IdeasSpace from "./components/views/IdeasSpace";
import Drawer from "./components/Drawer";
import AgentModal from "./components/AgentModal";
import FilterSheet from "./components/FilterSheet";
import type {
  Dir,
  Dsort,
  IdeaControls,
  IdeaSort,
  PmoControls,
  PmoSort,
  PmoStatus,
  View,
} from "./components/filterDefs";

const report = reportData as Report;

export default function App() {
  const data = useMemo(() => enrich(report), []);
  const puzzle = useMemo(() => buildPuzzle(data.pmoMeta, data.ideaMeta), [data]);

  const [view, setView] = useState<View>("map");

  // ПМО filters
  const [status, setStatus] = useState<PmoStatus>("all");
  const [minRel, setMinRel] = useState(0);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<PmoSort>("count");
  const [dir, setDir] = useState<Dir>("desc");

  // Идеи filters
  const [iSector, setISector] = useState("all");
  const [iFund, setIFund] = useState("all");
  const [iStage, setIStage] = useState("all");
  const [iQ, setIQ] = useState("");
  const [iSort, setISort] = useState<IdeaSort>("name");

  // drawer / modal / sheet
  const [drawer, setDrawer] = useState<{ kind: "agent" | "idea" | null; id: number | null }>({ kind: null, id: null });
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [dsort, setDsort] = useState<Dsort>("relevance");
  const [infoAgent, setInfoAgent] = useState<Agent | null>(null);
  const [filterSheetOpen, setFilterSheetOpen] = useState(false);

  // sticky-bar frost
  const [topScrolled, setTopScrolled] = useState(false);
  const [ctrlStuck, setCtrlStuck] = useState(false);

  // puzzle → space scroll target
  const [scrollTarget, setScrollTarget] = useState<{ key: string; t: number } | null>(null);
  const rafRef = useRef<number | null>(null);

  const pmo: PmoControls = { status, setStatus, minRel, setMinRel, q, setQ, sort, setSort, dir, setDir };
  const ideas: IdeaControls = {
    sector: iSector,
    setSector: setISector,
    fund: iFund,
    setFund: setIFund,
    stage: iStage,
    setStage: setIStage,
    q: iQ,
    setQ: setIQ,
    sort: iSort,
    setSort: setISort,
    sectors: data.ideaSectors,
    funds: data.ideaFunds,
    stages: data.ideaStages,
  };

  // ---------- ПМО list ----------
  const pmoSections = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const list = data.agents.filter((a) => {
      if (status === "ready" && a.status !== "Протестировать") return false;
      if (status === "dev" && a.status !== "В разработке") return false;
      if (a.avgRel < minRel) return false;
      if (needle && !(a.name.toLowerCase().includes(needle) || a.sredstvo.toLowerCase().includes(needle))) return false;
      return true;
    });
    const d = dir === "asc" ? 1 : -1;
    const rank = (s: string) => (s === "Протестировать" ? 1 : 0);
    const kf: Record<PmoSort, (a: (typeof list)[number]) => number | string> = {
      count: (a) => a.count,
      relevance: (a) => a.avgRel,
      pmo: (a) => a.avgPmo,
      name: (a) => a.name,
      status: (a) => rank(a.status),
    };
    const f = kf[sort];
    const sorted = [...list].sort((x, y) => {
      const xa = f(x);
      const ya = f(y);
      if (typeof xa === "string" && typeof ya === "string") return xa.localeCompare(ya, "ru") * d;
      return ((xa as number) - (ya as number)) * d;
    });
    return groupAgents(sorted);
  }, [data, status, minRel, q, sort, dir]);

  // ---------- Идеи list ----------
  const ideaSections = useMemo(() => {
    const needle = iQ.trim().toLowerCase();
    const arr = data.ideas.filter((s) => {
      if (iSector !== "all" && !s.sectors.includes(iSector)) return false;
      if (iFund !== "all" && s.fund !== iFund) return false;
      if (iStage !== "all" && s.stage !== iStage) return false;
      if (needle && !(s.name.toLowerCase().includes(needle) || s.description.toLowerCase().includes(needle))) return false;
      return true;
    });
    const ik: Record<IdeaSort, (a: Startup, b: Startup) => number> = {
      name: (a, b) => a.name.localeCompare(b.name, "ru"),
      pmo: (a, b) => b.pmoScore - a.pmoScore,
      year: (a, b) => (b.foundedYear ?? 0) - (a.foundedYear ?? 0),
      fund: (a, b) => a.fund.localeCompare(b.fund, "ru") || a.name.localeCompare(b.name, "ru"),
    };
    return groupIdeas([...arr].sort(ik[iSort]));
  }, [data, iSector, iFund, iStage, iQ, iSort]);

  const selAgent = drawer.kind === "agent" ? data.agents.find((a) => a.id === drawer.id) ?? null : null;
  const selIdea = drawer.kind === "idea" ? data.ideas.find((s) => s.id === drawer.id) ?? null : null;

  // ---------- handlers ----------
  const openAgent = (id: number) => {
    setDrawer({ kind: "agent", id });
    setDsort("relevance");
    setDrawerOpen(true);
  };
  const openIdea = (id: number) => {
    setDrawer({ kind: "idea", id });
    setDrawerOpen(true);
  };
  const closeDrawer = () => setDrawerOpen(false);

  const jump = (target: "pmo" | "ideas", name: string) => {
    setView(target);
    setScrollTarget({ key: `${target}::${name}`, t: Date.now() });
  };

  const resetFilters = () => {
    if (view === "pmo") {
      setStatus("all");
      setMinRel(0);
      setSort("count");
      setDir("desc");
    } else {
      setISector("all");
      setIFund("all");
      setIStage("all");
      setISort("name");
    }
  };

  // ---------- effects ----------
  useEffect(() => {
    const lock = drawerOpen || filterSheetOpen || !!infoAgent;
    document.body.style.overflow = lock ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen, filterSheetOpen, infoAgent]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (infoAgent) return; // AgentModal closes itself
      if (filterSheetOpen) setFilterSheetOpen(false);
      else if (drawerOpen) setDrawerOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [infoAgent, filterSheetOpen, drawerOpen]);

  useEffect(() => {
    const onScroll = () => {
      setTopScrolled((window.scrollY || 0) > 24);
      const bar = document.querySelector("[data-ctrlbar]");
      setCtrlStuck(bar ? bar.getBoundingClientRect().top <= 54 : false);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // smooth-scroll to a group section after a puzzle/accordion jump
  useEffect(() => {
    if (!scrollTarget) return;
    let canceled = false;
    const animate = (toY: number, duration = 640) => {
      const fromY = window.scrollY;
      const dist = toY - fromY;
      if (Math.abs(dist) < 2) {
        window.scrollTo(0, toY);
        return;
      }
      const start = performance.now();
      const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
      const step = (now: number) => {
        if (canceled) return;
        const p = Math.min(1, (now - start) / duration);
        window.scrollTo(0, Math.round(fromY + dist * ease(p)));
        if (p < 1) rafRef.current = requestAnimationFrame(step);
      };
      rafRef.current = requestAnimationFrame(step);
    };
    const r = requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        setTimeout(() => {
          if (canceled) return;
          const el = document.querySelector(`[data-group="${scrollTarget.key}"]`);
          if (!el) return;
          const tb = document.querySelector("header");
          const cb = document.querySelector("[data-ctrlbar]");
          const off = (tb instanceof HTMLElement ? tb.offsetHeight : 0) + (cb instanceof HTMLElement ? cb.offsetHeight : 0) + 18;
          const y = Math.max(0, Math.round(el.getBoundingClientRect().top + window.scrollY - off));
          animate(y);
        }, 90);
      }),
    );
    return () => {
      canceled = true;
      cancelAnimationFrame(r);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [scrollTarget]);

  const m = data.meta;

  return (
    <div className="relative min-h-screen overflow-x-clip">
      {/* ambient glow (desktop) */}
      <div aria-hidden className="pointer-events-none absolute -left-[160px] top-[430px] -z-[1] hidden h-[620px] w-[620px] rounded-full md:block" style={{ background: "radial-gradient(circle,rgba(63,138,120,.16),transparent 62%)" }} />
      <div aria-hidden className="pointer-events-none absolute -right-[140px] -top-[180px] -z-[1] hidden h-[600px] w-[600px] rounded-full md:block" style={{ background: "radial-gradient(circle,rgba(194,96,60,.20),transparent 64%)" }} />

      <Header scrolled={topScrolled} />
      <Hero meta={m} />
      <Controls view={view} setView={setView} ctrlStuck={ctrlStuck} pmo={pmo} ideas={ideas} openFilters={() => setFilterSheetOpen(true)} />

      <main className="mx-auto max-w-[1240px] px-[18px] pb-[56px] pt-[20px] md:px-[28px] md:pb-[70px] md:pt-[30px]">
        {view === "map" && <MapView puzzle={puzzle} pmoMeta={data.pmoMeta} ideaMeta={data.ideaMeta} onJump={jump} />}
        {view === "pmo" && <PmoSpace sections={pmoSections} onOpen={openAgent} noResults={pmoSections.length === 0} />}
        {view === "ideas" && <IdeasSpace sections={ideaSections} onOpen={openIdea} noResults={ideaSections.length === 0} />}
      </main>

      <Drawer
        open={drawerOpen}
        kind={drawer.kind}
        agent={selAgent}
        idea={selIdea}
        dsort={dsort}
        onDsort={setDsort}
        minRel={minRel}
        onClose={closeDrawer}
        onOpenInfo={setInfoAgent}
      />
      <AgentModal agent={infoAgent} onClose={() => setInfoAgent(null)} />
      {(view === "pmo" || view === "ideas") && (
        <FilterSheet open={filterSheetOpen} view={view} pmo={pmo} ideas={ideas} onClose={() => setFilterSheetOpen(false)} onReset={resetFilters} />
      )}
    </div>
  );
}
