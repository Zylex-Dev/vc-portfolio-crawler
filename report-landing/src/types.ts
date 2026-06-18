export type AgentStatus = "В разработке" | "Протестировать";

export interface PmoSub {
  traj: number;
  mat: number;
  collab: number;
  game: number;
  feedback: number;
}

export interface Agent {
  id: number;
  name: string;
  category: string; // средство-group (domain)
  sredstvo: string;
  status: AgentStatus;
  role: string;
  userStory: string;
  resourceLink: string;
  comment: string;
  functionalRequirements: string[];
  expectedBehavior: string;
  inputs: string;
  outputs: string;
  cjmClassroom: string;
  cjmPlatform: string;
}

export interface Startup {
  id: number;
  fund: string;
  name: string;
  sectors: string[];
  website: string;
  description: string;
  stage: string;
  foundedYear: number | null;
  pmoScore: number;
  pmoSub: PmoSub;
  relevance: number;
  rationale: string;
  assignedAgent: string; // agent name or "unmatched"
}

export interface ReportMeta {
  totalCollected: number;
  totalStartups: number;
  totalAgents: number;
  matched: number;
  unmatched: number;
  totalFunds: number;
}

export interface Report {
  meta: ReportMeta;
  agents: Agent[];
  startups: Startup[];
}

/** An agent enriched with its assigned startup group + group aggregates. */
export interface AgentGroup extends Agent {
  group: Startup[];
  count: number;
  avgRel: number;
  avgPmo: number;
  sub: PmoSub;
}

export const UNMATCHED = "unmatched";
