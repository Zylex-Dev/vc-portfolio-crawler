import type { ReportMeta } from "../types";
import { C, FONT_SERIF, fmtInt } from "../theme";

export default function Hero({ meta }: { meta: ReportMeta }) {
  const heroStats = [
    { v: fmtInt(meta.totalCollected), l: "стартапов собрано", color: C.ink },
    { v: fmtInt(meta.totalStartups), l: "EdTech отфильтровано", color: C.ink },
    { v: fmtInt(meta.totalAgents), l: "ИИ-агентов ПМО", color: C.ink },
    { v: fmtInt(meta.matched), l: "сматчено с агентами", color: C.teal },
    { v: fmtInt(meta.unmatched), l: "новых идей вне покрытия", color: C.clay },
    { v: fmtInt(meta.totalFunds), l: "венчурных фондов", color: C.ink },
  ];

  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="absolute inset-0 opacity-50" style={{ backgroundImage: "radial-gradient(#D9CDB6 1.1px,transparent 1.1px)", backgroundSize: "24px 24px" }} />
      <div className="absolute -top-[160px] -right-[120px] h-[520px] w-[520px] rounded-full" style={{ background: "radial-gradient(circle,rgba(194,96,60,.20),transparent 65%)" }} />
      <div className="absolute -bottom-[200px] -left-[100px] h-[480px] w-[480px] rounded-full" style={{ background: "radial-gradient(circle,rgba(63,138,120,.14),transparent 65%)" }} />
      <div className="relative mx-auto max-w-[1240px] px-[28px] pb-[40px] pt-[64px] [animation:fadeUp_.5s_both]">
        <div className="mb-[24px] inline-flex items-center gap-[8px] rounded-full border border-border bg-white px-[14px] py-[6px] text-[12.5px] font-semibold text-[#9A6A4A]">
          <span className="h-[7px] w-[7px] rounded-full bg-clay" />
          Исследование венчурных портфелей 2026
        </div>
        <h1 className="m-0 mb-[18px] text-[54px] font-normal leading-[1.04] tracking-[-.015em]" style={{ fontFamily: FONT_SERIF }}>
          Лучшие мировые практики EdTech&nbsp;стартапов для воплощения ПМО на практике
        </h1>
        <p className="m-0 mb-[40px] max-w-[62ch] text-[18px] font-normal leading-[1.55] text-ink-soft">
          Мы собрали <b className="font-bold text-ink">{fmtInt(meta.totalCollected)}</b> стартапов из портфелей крупных венчурных фондов,
          отфильтровали <b className="font-bold text-ink">{fmtInt(meta.totalStartups)}</b> EdTech-решений и сопоставили каждое
          с <b className="font-bold text-ink">{meta.totalAgents}</b> ИИ-агентами персонализированной модели образования.
          Ниже — интерактивная карта совпадений и зона новых идей.
        </p>
        <div className="grid gap-px overflow-hidden rounded-[18px] border border-border bg-border" style={{ gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))" }}>
          {heroStats.map((s) => (
            <div key={s.l} className="bg-card px-[22px] pb-[20px] pt-[22px]">
              <div className="text-[34px] leading-none tracking-[-.02em] [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF, color: s.color }}>{s.v}</div>
              <div className="mt-[8px] text-[12.5px] font-medium leading-[1.35] text-[#837A6C]">{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
