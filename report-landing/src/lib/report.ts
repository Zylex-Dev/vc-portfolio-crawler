import type { AgentGroup, PmoSub, Report, Startup } from "../types";
import { IDEA_GROUP_ORDER, SREDSTVO_ORDER, UNMATCHED } from "../types";

const round1 = (n: number) => Math.round(n * 10) / 10;

function avg(arr: Startup[], f: (s: Startup) => number): number {
  if (!arr.length) return 0;
  return round1(arr.reduce((acc, s) => acc + f(s), 0) / arr.length);
}

function subOf(group: Startup[]): PmoSub {
  return {
    traj: avg(group, (s) => s.pmoSub.traj),
    mat: avg(group, (s) => s.pmoSub.mat),
    collab: avg(group, (s) => s.pmoSub.collab),
    game: avg(group, (s) => s.pmoSub.game),
    feedback: avg(group, (s) => s.pmoSub.feedback),
  };
}

/** A puzzle-map slot: a group label with its item count. */
export interface GroupMeta {
  name: string;
  count: number;
}

/** A rendered section: ПМО средство (agents) or idea niche (startups). */
export interface Section<T> {
  name: string;
  idx: string; // "01", "02", … over *shown* sections only
  count: number;
  items: T[];
}

export interface EnrichedReport {
  meta: Report["meta"];
  agents: AgentGroup[]; // all 44 agents, enriched with their startup group
  ideas: Startup[]; // 232 unmatched "new idea" startups
  pmoMeta: GroupMeta[]; // 5 средства + agent counts (puzzle / baseline)
  ideaMeta: GroupMeta[]; // 7 niches + startup counts
  ideaSectors: string[];
  ideaFunds: string[];
  ideaStages: string[];
}

// Known funding stages float to the top of the filter; messy values trail behind.
const STAGE_ORDER = ["Pre-Seed", "Pre-Seed/Seed", "Seed", "Series A", "Series B", "Series C", "Series D", "Growth"];

/** Group startups under their assigned agent and precompute everything the UI needs. */
export function enrich(report: Report): EnrichedReport {
  const byAgent = new Map<string, Startup[]>();
  report.agents.forEach((a) => byAgent.set(a.name, []));

  const ideas: Startup[] = [];
  report.startups.forEach((s) => {
    const bucket = byAgent.get(s.assignedAgent);
    if (s.assignedAgent !== UNMATCHED && bucket) bucket.push(s);
    else ideas.push(s);
  });

  const agents: AgentGroup[] = report.agents.map((a) => {
    const group = byAgent.get(a.name) ?? [];
    return {
      ...a,
      group,
      count: group.length,
      avgRel: avg(group, (s) => s.relevance),
      avgPmo: avg(group, (s) => s.pmoScore),
      sub: subOf(group),
    };
  });

  const pmoMeta: GroupMeta[] = SREDSTVO_ORDER.map((name) => ({
    name,
    count: agents.filter((a) => a.sredstvo === name).length,
  }));
  const ideaMeta: GroupMeta[] = IDEA_GROUP_ORDER.map((name) => ({
    name,
    count: ideas.filter((s) => s.functionalGroup === name).length,
  }));

  const ideaSectors = [...new Set(ideas.flatMap((s) => s.sectors))].sort((a, b) => a.localeCompare(b, "ru"));
  const ideaFunds = [...new Set(ideas.map((s) => s.fund))].sort((a, b) => a.localeCompare(b, "ru"));
  const stageSet = new Set(ideas.map((s) => s.stage).filter(Boolean));
  const ideaStages = [
    ...STAGE_ORDER.filter((s) => stageSet.has(s)),
    ...[...stageSet].filter((s) => !STAGE_ORDER.includes(s)).sort((a, b) => a.localeCompare(b, "ru")),
  ];

  return { meta: report.meta, agents, ideas, pmoMeta, ideaMeta, ideaSectors, ideaFunds, ideaStages };
}

/** Bucket already-filtered agents into their 5 средства, numbering shown sections. */
export function groupAgents(agents: AgentGroup[]): Section<AgentGroup>[] {
  return numberSections(
    SREDSTVO_ORDER.map((name) => ({ name, items: agents.filter((a) => a.sredstvo === name) })),
  );
}

/** Bucket already-filtered ideas into their 7 niches, numbering shown sections. */
export function groupIdeas(ideas: Startup[]): Section<Startup>[] {
  return numberSections(
    IDEA_GROUP_ORDER.map((name) => ({ name, items: ideas.filter((s) => s.functionalGroup === name) })),
  );
}

function numberSections<T>(raw: { name: string; items: T[] }[]): Section<T>[] {
  return raw
    .filter((g) => g.items.length)
    .map((g, i) => ({ name: g.name, idx: String(i + 1).padStart(2, "0"), count: g.items.length, items: g.items }));
}
