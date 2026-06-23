import { useLayoutEffect, useRef, useState } from "react";
import { FONT_SERIF, LEGEND, PUZZLE } from "../../theme";
import type { GroupMeta } from "../../lib/report";
import type { Puzzle, Side } from "../../lib/puzzle";

type Jump = (view: "pmo" | "ideas", name: string) => void;

/** Карта — interlocking puzzle on desktop, two accordion lists on mobile. */
export default function MapView({
  puzzle,
  pmoMeta,
  ideaMeta,
  onJump,
}: {
  puzzle: Puzzle;
  pmoMeta: GroupMeta[];
  ideaMeta: GroupMeta[];
  onJump: Jump;
}) {
  // scale the fixed-size board down to fit the content column (no horizontal scroll)
  const boardRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  useLayoutEffect(() => {
    const el = boardRef.current;
    if (!el) return;
    const update = () => {
      if (el.clientWidth > 0) setScale(Math.min(1, el.clientWidth / puzzle.W));
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [puzzle.W]);

  return (
    <div className="animate-viewIn">
      <h2
        className="m-0 mb-[22px] text-[26px] font-normal leading-[1.1] tracking-[-.015em] md:mx-auto md:mb-[30px] md:max-w-[720px] md:text-center md:text-[38px] md:leading-[1.08]"
        style={{ fontFamily: FONT_SERIF }}
      >
        Карта исследования лучших практик
      </h2>

      {/* ---------- desktop puzzle ---------- */}
      <div className="hidden md:block" ref={boardRef}>
        <div className="mx-auto mb-[16px] flex max-w-[1000px] items-end justify-between gap-[24px]">
          <LegendItem color={LEGEND.pmo} text="Пространство ПМО" />
          <LegendItem color={LEGEND.idea} text="Пространство новых идей" reverse />
        </div>

        <div className="relative" style={{ height: Math.round(puzzle.H * scale) }}>
          <div
            style={{
              position: "absolute",
              top: 0,
              left: "50%",
              width: puzzle.W,
              height: puzzle.H,
              transform: `translateX(-50%) scale(${scale})`,
              transformOrigin: "top center",
            }}
          >
            {puzzle.pieces.map((p) => {
              const col = p.side === "pmo" ? PUZZLE.pmo : PUZZLE.idea;
              return (
                <button
                  key={p.id}
                  onClick={() => onJump(sideToView(p.side), p.label)}
                  className="puzzle-piece absolute cursor-pointer border-none bg-transparent p-0"
                  style={{ left: p.left, top: p.top, width: p.w, height: p.h, fontFamily: "inherit" }}
                >
                  <svg
                    viewBox={p.vb}
                    width={p.svgW}
                    height={p.svgH}
                    style={{ position: "absolute", left: p.svgLeft, top: p.svgTop, overflow: "visible", display: "block" }}
                  >
                    <defs>
                      <linearGradient id={p.gid} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0" stopColor={col.c1} />
                        <stop offset="1" stopColor={col.c2} />
                      </linearGradient>
                    </defs>
                    <path d={p.path} fill={`url(#${p.gid})`} stroke={col.stroke} strokeWidth={2.25} strokeLinejoin="round" />
                  </svg>
                  <span className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center gap-[6px] p-[10px] text-center">
                    {/* fixed-height wrapper so counter stays on the same line across all pieces */}
                    <span className="flex h-[80px] items-center justify-center">
                      <span
                        className="max-w-[184px] break-words text-[15.5px] font-bold leading-[1.2] tracking-[-.01em] [text-wrap:balance]"
                        style={{ color: col.text }}
                      >
                        {p.label}
                      </span>
                    </span>
                    <span
                      className="whitespace-nowrap text-[12.5px] font-bold tracking-[.02em] [font-variant-numeric:tabular-nums]"
                      style={{ color: col.meta }}
                    >
                      {p.count} {p.unit}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ---------- mobile accordion ---------- */}
      <div className="md:hidden">
        <AccordionLabel color={LEGEND.pmo} text="Пространство ПМО" />
        <div className="mb-[26px] flex flex-col gap-[9px]">
          {pmoMeta.map((g, i) => (
            <AccordionRow
              key={g.name}
              idx={i + 1}
              name={g.name}
              count={g.count}
              unit="агентов"
              onClick={() => onJump("pmo", g.name)}
              palette={{ bg: "#FBF4EB", border: "#E8C9A8", idx: "#A9744E", name: "#894A2D", meta: "#A9744E", arrow: "#C2603C" }}
            />
          ))}
        </div>

        <AccordionLabel color={LEGEND.idea} text="Пространство новых идей" />
        <div className="flex flex-col gap-[9px]">
          {ideaMeta.map((g, i) => (
            <AccordionRow
              key={g.name}
              idx={i + 1}
              name={g.name}
              count={g.count}
              unit="стартапов"
              onClick={() => onJump("ideas", g.name)}
              palette={{ bg: "#F2F8F3", border: "#B7D2C8", idx: "#4E8C75", name: "#2D6A54", meta: "#4E8C75", arrow: "#3F8A78" }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

const sideToView = (s: Side): "pmo" | "ideas" => (s === "pmo" ? "pmo" : "ideas");

function LegendItem({ color, text, reverse }: { color: { bg: string; border: string }; text: string; reverse?: boolean }) {
  return (
    <div className={`flex items-center gap-[10px] ${reverse ? "flex-row-reverse text-right" : ""}`}>
      <span className="h-[11px] w-[11px] flex-none rounded-[3px]" style={{ background: color.bg, border: `1.5px solid ${color.border}` }} />
      <span className="text-[20px] leading-[1.1] tracking-[-.01em] text-ink" style={{ fontFamily: FONT_SERIF }}>
        {text}
      </span>
    </div>
  );
}

function AccordionLabel({ color, text }: { color: { bg: string; border: string }; text: string }) {
  return (
    <div className="mb-[12px] flex items-center gap-[9px]">
      <span className="h-[11px] w-[11px] flex-none rounded-[3px]" style={{ background: color.bg, border: `1.5px solid ${color.border}` }} />
      <span className="text-[19px] leading-[1.1] tracking-[-.01em]" style={{ fontFamily: FONT_SERIF }}>
        {text}
      </span>
    </div>
  );
}

interface RowPalette {
  bg: string;
  border: string;
  idx: string;
  name: string;
  meta: string;
  arrow: string;
}

function AccordionRow({
  idx,
  name,
  count,
  unit,
  onClick,
  palette,
}: {
  idx: number;
  name: string;
  count: number;
  unit: string;
  onClick: () => void;
  palette: RowPalette;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-[13px] rounded-[15px] border px-[16px] py-[15px] text-left"
      style={{ background: palette.bg, borderColor: palette.border }}
    >
      <span className="flex-none text-[15px] [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF, color: palette.idx }}>
        {String(idx).padStart(2, "0")}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-[15px] font-bold leading-[1.25] tracking-[-.01em]" style={{ color: palette.name }}>
          {name}
        </span>
        <span className="mt-[3px] block text-[12px] font-semibold [font-variant-numeric:tabular-nums]" style={{ color: palette.meta }}>
          {count} {unit}
        </span>
      </span>
      <span className="flex-none text-[17px] font-bold" style={{ color: palette.arrow }}>
        →
      </span>
    </button>
  );
}
