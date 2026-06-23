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
  investedYear: number | null;
  pmoScore: number;
  pmoSub: PmoSub;
  relevance: number;
  rationale: string;
  assignedAgent: string; // agent name or "unmatched"
  functionalGroup: string | null; // one of 7 niches (unmatched only)
  groupRationale: string; // per-startup niche rationale (unmatched only)
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

/** The 5 ПМО средства — agent grouping + left side of the puzzle map. */
export const SREDSTVO_ORDER = [
  "Персонализированная траектория",
  "Учебные материалы",
  "Совместная деятельность и общение",
  "Геймификация и визуализация",
  "Обратная связь",
] as const;

/** The 7 "new idea" niches (G1–G7) — right side of the puzzle map. */
export const IDEA_GROUP_ORDER = [
  "Комплексные платформы, школы и курсы",
  "Живое обучение и репетиторы",
  "Карьера, трудоустройство и профориентация",
  "Контент, учебные программы и обучающие инструменты",
  "Управление, данные и финансы",
  "Поддержка участников (семья, благополучие, педагоги, сообщество)",
  "Прочее / смежные нишевые сервисы",
] as const;
