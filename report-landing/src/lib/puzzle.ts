import type { GroupMeta } from "./report";

/**
 * Interlocking 4×3 puzzle map, ported verbatim from the Claude Design mockup.
 * Left 5 cells = ПМО средства, right 7 cells = idea niches. Each internal seam
 * carries a symmetric "mushroom" tab so neighbouring pieces interlock.
 */

export type Side = "pmo" | "idea";

export interface PuzzlePiece {
  id: string;
  side: Side;
  /** absolute position of the cell (px) inside the W×H board */
  left: number;
  top: number;
  w: number;
  h: number;
  /** the SVG is oversized by T on every edge so tabs aren't clipped */
  svgLeft: number;
  svgTop: number;
  svgW: number;
  svgH: number;
  vb: string;
  path: string;
  gid: string;
  label: string;
  count: number;
  unit: string;
}

export interface Puzzle {
  W: number;
  H: number;
  pieces: PuzzlePiece[];
}

type Seg =
  | { t: "L"; p: [number, number] }
  | { t: "C"; p: [[number, number], [number, number], [number, number]] };

interface Pt {
  x: number;
  y: number;
}

export function buildPuzzle(pmoMeta: GroupMeta[], ideaMeta: GroupMeta[]): Puzzle {
  const cols = 4;
  const rows = 3;
  const cellW = 250;
  const cellH = 210;
  const T = 32;
  const Ht = 32;
  const W = cols * cellW;
  const H = rows * cellH;

  // 5 PMO on the left, 7 ideas on the right — a jagged seam down the middle.
  const sideGrid: Side[][] = [
    ["pmo", "idea", "idea", "idea"],
    ["pmo", "pmo", "idea", "idea"],
    ["pmo", "pmo", "idea", "idea"],
  ];

  // internal-edge orientation so adjacent tabs are complementary
  const vSign = (r: number, c: number) => ((r + c) % 2 ? 1 : -1);
  const hSign = (r: number, c: number) => ((r + c) % 2 ? -1 : 1);
  const rnd = (v: number) => Math.round(v * 100) / 100;

  // symmetric mushroom tab, normalized (u along edge 0..1, v outward 0..~1)
  const SEGS: Seg[] = [
    { t: "L", p: [0.36, 0] },
    { t: "C", p: [[0.31, 0.18], [0.28, 0.55], [0.36, 0.8]] },
    { t: "C", p: [[0.4, 1.06], [0.6, 1.06], [0.64, 0.8]] },
    { t: "C", p: [[0.72, 0.55], [0.69, 0.18], [0.64, 0]] },
    { t: "L", p: [1, 0] },
  ];

  const edge = (P0: Pt, P1: Pt, s: number, nx: number, ny: number): string => {
    const ax = P1.x - P0.x;
    const ay = P1.y - P0.y;
    const L = Math.hypot(ax, ay);
    const ux = ax / L;
    const uy = ay / L;
    const map = (u: number, v: number): Pt => ({
      x: P0.x + ux * (u * L) + nx * (s * v * Ht),
      y: P0.y + uy * (u * L) + ny * (s * v * Ht),
    });
    let d = "";
    for (const seg of SEGS) {
      if (seg.t === "L") {
        const q = map(seg.p[0], seg.p[1]);
        d += `L ${rnd(q.x)} ${rnd(q.y)} `;
      } else {
        const a = map(seg.p[0][0], seg.p[0][1]);
        const b = map(seg.p[1][0], seg.p[1][1]);
        const c = map(seg.p[2][0], seg.p[2][1]);
        d += `C ${rnd(a.x)} ${rnd(a.y)} ${rnd(b.x)} ${rnd(b.y)} ${rnd(c.x)} ${rnd(c.y)} `;
      }
    }
    return d;
  };

  const pieces: PuzzlePiece[] = [];
  let pmoI = 0;
  let ideaI = 0;
  const empty: GroupMeta = { name: "", count: 0 };

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const side = sideGrid[r][c];
      const top = r === 0 ? 0 : -hSign(r - 1, c);
      const bottom = r === rows - 1 ? 0 : hSign(r, c);
      const left = c === 0 ? 0 : -vSign(r, c - 1);
      const right = c === cols - 1 ? 0 : vSign(r, c);
      const TL = { x: T, y: T };
      const TR = { x: T + cellW, y: T };
      const BR = { x: T + cellW, y: T + cellH };
      const BL = { x: T, y: T + cellH };
      let d = `M ${TL.x} ${TL.y} `;
      d += edge(TL, TR, top, 0, -1); // top, outward up
      d += edge(TR, BR, right, 1, 0); // right, outward right
      d += edge(BR, BL, bottom, 0, 1); // bottom, outward down
      d += edge(BL, TL, left, -1, 0); // left, outward left
      d += "Z";
      const meta = side === "pmo" ? pmoMeta[pmoI++] ?? empty : ideaMeta[ideaI++] ?? empty;
      const svgW = cellW + 2 * T;
      const svgH = cellH + 2 * T;
      pieces.push({
        id: `${r}-${c}`,
        side,
        left: c * cellW,
        top: r * cellH,
        w: cellW,
        h: cellH,
        svgLeft: -T,
        svgTop: -T,
        svgW,
        svgH,
        vb: `0 0 ${svgW} ${svgH}`,
        path: d,
        gid: `pz${r}${c}`,
        label: meta.name,
        count: meta.count,
        unit: side === "pmo" ? "агентов" : "стартапов",
      });
    }
  }

  return { W, H, pieces };
}
