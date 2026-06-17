import type { Agent, AgentGroup, PmoSub, Report, Startup } from "../types";
import { UNMATCHED } from "../types";

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

export interface UnmatchedBucket {
  group: Startup[];
  count: number;
  avgRel: number;
  avgPmo: number;
  sub: PmoSub;
  topSectors: string[];
}

export interface EnrichedReport {
  meta: Report["meta"];
  agents: AgentGroup[];
  maxCount: number;
  unmatched: UnmatchedBucket;
}

/** Group startups under their assigned agent and compute group aggregates. */
export function enrich(report: Report): EnrichedReport {
  const byAgent = new Map<string, Startup[]>();
  report.agents.forEach((a: Agent) => byAgent.set(a.name, []));

  const unmatchedStartups: Startup[] = [];
  report.startups.forEach((s) => {
    const bucket = byAgent.get(s.assignedAgent);
    if (s.assignedAgent !== UNMATCHED && bucket) bucket.push(s);
    else unmatchedStartups.push(s);
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

  const maxCount = Math.max(1, ...agents.map((a) => a.count));

  // Count sectors case-insensitively; keep the most frequent original spelling
  // as the display label (raw data mixes "Education" / "education").
  const secCount = new Map<string, { total: number; labels: Map<string, number> }>();
  unmatchedStartups.forEach((s) =>
    s.sectors.forEach((sec) => {
      const key = sec.toLowerCase();
      const entry = secCount.get(key) ?? { total: 0, labels: new Map<string, number>() };
      entry.total += 1;
      entry.labels.set(sec, (entry.labels.get(sec) ?? 0) + 1);
      secCount.set(key, entry);
    }),
  );
  const topSectors = [...secCount.values()]
    .sort((a, b) => b.total - a.total)
    .slice(0, 4)
    .map((e) => [...e.labels.entries()].sort((a, b) => b[1] - a[1])[0][0]);

  return {
    meta: report.meta,
    agents,
    maxCount,
    unmatched: {
      group: unmatchedStartups,
      count: unmatchedStartups.length,
      avgRel: avg(unmatchedStartups, (s) => s.relevance),
      avgPmo: avg(unmatchedStartups, (s) => s.pmoScore),
      sub: subOf(unmatchedStartups),
      topSectors,
    },
  };
}
