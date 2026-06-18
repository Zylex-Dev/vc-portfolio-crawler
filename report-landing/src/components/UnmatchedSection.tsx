import type { Startup } from "../types";
import type { UnmatchedBucket } from "../lib/report";
import { FONT_SERIF, fmt1, fmtInt } from "../theme";
import { metaLine } from "./shared";
import { clamp } from "../lib/text";

export default function UnmatchedSection({ unmatched, onOpen }: { unmatched: UnmatchedBucket; onOpen: () => void }) {
  const samples: Startup[] = [...unmatched.group].sort((a, b) => b.pmoScore - a.pmoScore).slice(0, 4);
  return (
    <section className="relative mt-[46px] overflow-hidden rounded-[24px] border border-[#E6CDB8]" style={{ background: "linear-gradient(135deg,#FBEDE2,#F7F0E4)" }}>
      <div className="absolute -top-[90px] -right-[60px] h-[340px] w-[340px] rounded-full" style={{ background: "radial-gradient(circle,rgba(194,96,60,.16),transparent 65%)" }} />
      <div className="relative px-[32px] py-[34px]">
        <div className="mb-[26px] flex flex-wrap items-end justify-between gap-[20px]">
          <div className="max-w-[54ch]">
            <div className="mb-[16px] inline-flex items-center gap-[8px] rounded-full border border-[#E6CDB8] bg-white px-[13px] py-[5px] text-[12px] font-bold text-clay-deep">
              <span className="h-[7px] w-[7px] rounded-full bg-clay" />
              Зона новых идей
            </div>
            <h2 className="m-0 mb-[10px] text-[30px] font-normal leading-[1.1] tracking-[-.015em]" style={{ fontFamily: FONT_SERIF }}>
              {fmtInt(unmatched.count)} стартапов вне покрытия 44 агентов
            </h2>
            <p className="m-0 text-[15px] font-normal leading-[1.55] text-prose">
              Эти команды не совпали ни с одним нашим агентом — самый ценный срез исследования. Каждый из них — кандидат на новую продуктовую гипотезу для пайплайна ПМО.
            </p>
          </div>
          <button onClick={onOpen} className="cursor-pointer whitespace-nowrap rounded-full border-none bg-clay px-[22px] py-[13px] text-[14px] font-bold text-white" style={{ boxShadow: "0 8px 20px -8px rgba(194,96,60,.6)" }}>
            Смотреть все {fmtInt(unmatched.count)} →
          </button>
        </div>
        <div className="mb-[22px] flex flex-wrap gap-[10px]">
          <div className="rounded-[13px] border border-[#EBDCC9] bg-white px-[18px] py-[13px]">
            <div className="text-[25px] leading-none text-teal [font-variant-numeric:tabular-nums]" style={{ fontFamily: FONT_SERIF }}>{fmt1(unmatched.avgPmo)}</div>
            <div className="mt-[5px] text-[11.5px] font-semibold text-[#9A8F7C]">среднее соответствие ПМО 2.0</div>
          </div>
          {unmatched.topSectors.map((s) => (
            <div key={s} className="flex flex-col justify-center rounded-[13px] border border-[#EBDCC9] bg-white px-[18px] py-[13px]">
              <div className="text-[14px] font-bold text-ink">{s}</div>
              <div className="mt-[4px] text-[11.5px] font-semibold text-[#9A8F7C]">частый сектор</div>
            </div>
          ))}
        </div>
        <div className="grid gap-[12px]" style={{ gridTemplateColumns: "repeat(auto-fill,minmax(250px,1fr))" }}>
          {samples.map((s) => (
            <div key={s.id} className="rounded-[15px] border border-[#EBDCC9] bg-white p-[16px]">
              <div className="text-[15.5px] font-bold tracking-[-.01em]">{s.name}</div>
              <div className="my-[7px] mb-[9px] text-[12px] font-semibold text-faint">{metaLine(s)}</div>
              <div className="text-[12.5px] leading-[1.45] text-prose">{clamp(s.description, 160)}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
