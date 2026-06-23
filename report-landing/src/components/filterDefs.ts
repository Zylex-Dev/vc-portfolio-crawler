/** Shared filter/sort vocabulary for the ПМО + Идеи controls (desktop bar & mobile sheet). */

export type View = "map" | "pmo" | "ideas";
export type PmoStatus = "all" | "ready" | "dev";
export type PmoSort = "count" | "relevance" | "pmo" | "name" | "status";
export type IdeaSort = "name" | "pmo" | "year" | "fund";
export type Dir = "asc" | "desc";
export type Dsort = "relevance" | "pmo" | "year" | "name";

export const VIEWS: { k: View; full: string; short: string }[] = [
  { k: "map", full: "Карта", short: "Карта" },
  { k: "pmo", full: "Пространство ПМО", short: "ПМО" },
  { k: "ideas", full: "Пространство новых идей", short: "Новые идеи" },
];

export const STATUS_CHIPS: { v: PmoStatus; label: string; dot: string }[] = [
  { v: "all", label: "Все", dot: "transparent" },
  { v: "ready", label: "Готов MVP", dot: "#3F7D55" },
  { v: "dev", label: "В разработке", dot: "#A9781F" },
];

export const PMO_SORTS: { v: PmoSort; label: string }[] = [
  { v: "count", label: "По размеру группы" },
  { v: "relevance", label: "По релевантности" },
  { v: "pmo", label: "По соответствию ПМО 2.0" },
  { v: "name", label: "По названию" },
  { v: "status", label: "По статусу" },
];

export const IDEA_SORTS: { v: IdeaSort; label: string }[] = [
  { v: "name", label: "По названию" },
  { v: "pmo", label: "По соответствию ПМО 2.0" },
  { v: "year", label: "По году основания" },
  { v: "fund", label: "По фонду" },
];

export const DSORTS: { v: Dsort; label: string }[] = [
  { v: "relevance", label: "релевантность" },
  { v: "pmo", label: "соответствие ПМО" },
  { v: "year", label: "год основания" },
  { v: "name", label: "название" },
];

/** Filter state + setters bundled so they can flow to both the bar and the sheet. */
export interface PmoControls {
  status: PmoStatus;
  setStatus: (v: PmoStatus) => void;
  minRel: number;
  setMinRel: (v: number) => void;
  q: string;
  setQ: (v: string) => void;
  sort: PmoSort;
  setSort: (v: PmoSort) => void;
  dir: Dir;
  setDir: (v: Dir) => void;
}

export interface IdeaControls {
  sector: string;
  setSector: (v: string) => void;
  fund: string;
  setFund: (v: string) => void;
  stage: string;
  setStage: (v: string) => void;
  q: string;
  setQ: (v: string) => void;
  sort: IdeaSort;
  setSort: (v: IdeaSort) => void;
  sectors: string[];
  funds: string[];
  stages: string[];
}

export const pmoHasFilters = (p: PmoControls) => p.status !== "all" || p.minRel > 0;
export const ideaHasFilters = (i: IdeaControls) =>
  i.sector !== "all" || i.fund !== "all" || i.stage !== "all";
