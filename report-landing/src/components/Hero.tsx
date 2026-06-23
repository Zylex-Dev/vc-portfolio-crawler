import type { ReportMeta } from "../types";
import { C, FONT_SERIF } from "../theme";

const U = "./uploads";

/** Scattered fund logos (desktop) — absolute placement ported from the mockup. */
const SCATTER = [
  { href: "https://www.sequoiacap.com", src: `${U}/Sequoia_Capital_logo.svg`, alt: "Sequoia Capital", left: "1%", top: 6, w: 158, rot: -3, pad: "15px 17px" },
  { href: "https://a16z.com", src: `${U}/Andreessen_Horowitz_new_logo.svg`, alt: "Andreessen Horowitz", left: "58%", top: 16, w: 150, rot: 4, pad: "15px 17px" },
  { href: "https://www.reachcapital.com", src: `${U}/Reach_Capital_id_BpkAc74_1.svg`, alt: "Reach Capital", left: "4%", top: 128, w: 150, rot: 3, pad: "15px 17px" },
  { href: "https://owlvc.com", src: `${U}/owl-ventures-seeklogo.svg`, alt: "Owl Ventures", left: "64%", top: 152, w: 126, rot: 6, pad: "14px 16px" },
  { href: "https://speedrun.a16z.com/", src: `${U}/a16z_speedrun_logo.png`, alt: "a16z Speedrun", left: "30%", top: 212, w: 150, rot: -3, pad: "9px", imgRadius: 9 },
  { href: "https://gsv.ventures/portfolio/", src: `${U}/GSV_Ventures_logo.jpeg`, alt: "GSV Ventures", left: "3%", top: 250, w: 90, rot: -7, pad: "9px", imgRadius: 9 },
  { href: "https://www.brighteyevc.com", src: `${U}/Brighteye_Ventures_idqAGmsKRd_1.svg`, alt: "BrightEye Ventures", left: "50%", top: 330, w: 178, rot: 3, pad: "15px 17px" },
  { href: "https://learncapital.com", src: `${U}/Learn_Capital_idQerHWJE8_1.svg`, alt: "Learn Capital", left: "6%", top: 362, w: 132, rot: -4, pad: "14px 16px" },
  { href: "https://educapital.fr", src: `${U}/Educapital_id-NGg4dhB_1.svg`, alt: "EduCapital", left: "38%", top: 472, w: 148, rot: -4, pad: "15px 17px", dark: true },
  { href: "https://www.newschools.org", src: `${U}/NewSchools_logo.jpeg`, alt: "NewSchools Venture Fund", left: "1%", top: 478, w: 86, rot: 5, pad: "9px", imgRadius: 9 },
  { href: "https://www.ycombinator.com", src: `${U}/Y_Combinator_idmMYQweGN_0.svg`, alt: "Y Combinator", left: "66%", top: 512, w: 138, rot: -3, pad: "15px 17px" },
];

/** Logos used in the mobile marquee (image heights tuned per logo). */
const MARQUEE = [
  { href: "https://www.sequoiacap.com", src: `${U}/Sequoia_Capital_logo.svg`, alt: "Sequoia", h: 18 },
  { href: "https://a16z.com", src: `${U}/Andreessen_Horowitz_new_logo.svg`, alt: "a16z", h: 22 },
  { href: "https://www.reachcapital.com", src: `${U}/Reach_Capital_id_BpkAc74_1.svg`, alt: "Reach", h: 18 },
  { href: "https://owlvc.com", src: `${U}/owl-ventures-seeklogo.svg`, alt: "Owl", h: 24 },
  { href: "https://www.brighteyevc.com", src: `${U}/Brighteye_Ventures_idqAGmsKRd_1.svg`, alt: "BrightEye", h: 18 },
  { href: "https://learncapital.com", src: `${U}/Learn_Capital_idQerHWJE8_1.svg`, alt: "Learn", h: 18 },
  { href: "https://educapital.fr", src: `${U}/Educapital_id-NGg4dhB_1.svg`, alt: "EduCapital", h: 18, dark: true },
  { href: "https://www.ycombinator.com", src: `${U}/Y_Combinator_idmMYQweGN_0.svg`, alt: "Y Combinator", h: 18 },
];

const numStyle: React.CSSProperties = {
  fontFamily: FONT_SERIF,
  fontWeight: 500,
  color: C.clay,
  letterSpacing: "-.025em",
  fontVariantNumeric: "tabular-nums",
};
const Num = ({ children, cls }: { children: React.ReactNode; cls: string }) => (
  <span className={cls} style={numStyle}>
    {children}
  </span>
);

export default function Hero({ meta }: { meta: ReportMeta }) {
  const { totalFunds, totalCollected, matched, unmatched } = meta;

  return (
    <section className="relative overflow-hidden">
      {/* dotted paper texture */}
      <div
        className="absolute inset-0 opacity-[.45] md:opacity-50"
        style={{ backgroundImage: "radial-gradient(#D9CDB6 1.1px,transparent 1.1px)", backgroundSize: "20px 20px" }}
      />

      <div className="relative mx-auto max-w-[1240px] px-[18px] pb-[22px] pt-[24px] md:px-[28px] md:py-[40px]">
        <div className="flex flex-wrap items-center gap-[48px]">
          {/* LEFT — copy */}
          <div className="min-w-[300px] flex-[1_1_520px] md:max-w-[640px]">
            <h1
              className="m-0 mb-[14px] text-[30px] font-normal leading-[1.08] tracking-[-.015em] md:mb-[20px] md:text-[48px] md:leading-[1.06]"
              style={{ fontFamily: FONT_SERIF }}
            >
              Лучшие мировые практики EdTech&#8209;стартапов для воплощения ПМО на практике
            </h1>

            {/* mobile copy (shorter) */}
            <p className="m-0 text-[15px] font-[450] leading-[1.62] text-[#4A4236] md:hidden">
              Из портфелей <Num cls="text-[1.7em]">{totalFunds}</Num> крупнейших венчурных фондов мы собрали{" "}
              <Num cls="text-[1.7em]">{totalCollected}</Num> самых перспективных ИИ стартапов в мире.{" "}
              <Num cls="text-[1.7em]">{matched}</Num> идей легли в описание агентов ПМО, а{" "}
              <Num cls="text-[1.7em]">{unmatched}</Num> новых идеи дополняют картину мирового EdTech рынка.
            </p>

            {/* desktop copy (full) */}
            <p className="m-0 hidden text-[20px] font-[450] leading-[1.72] text-[#4A4236] md:block">
              Из портфелей <Num cls="text-[1.95em]">{totalFunds}</Num> крупнейших венчурных фондов мы собрали{" "}
              <Num cls="text-[1.95em]">{totalCollected}</Num> самых перспективных ИИ стартапов в мире. С помощью метода
              LLM&#8209;as&#8209;a&#8209;Judge обогатили функционал целевых ИИ&#8209;Агентов ПМО, планируемых к
              тестированию. <Num cls="text-[1.95em]">{matched}</Num> идей стартапов легли в описание агентов,
              используемых в ПМО. <Num cls="text-[1.95em]">{unmatched}</Num> новых идеи позволяют дополнить картину
              перспективных технологий мирового EdTech рынка.
            </p>

            {/* mobile marquee */}
            <div
              className="mt-[20px] overflow-hidden md:hidden"
              style={{
                WebkitMaskImage: "linear-gradient(90deg,transparent,#000 24px,#000 calc(100% - 24px),transparent)",
                maskImage: "linear-gradient(90deg,transparent,#000 24px,#000 calc(100% - 24px),transparent)",
              }}
            >
              <div className="marquee-scroll flex w-max">
                {[...MARQUEE, ...MARQUEE].map((l, i) => (
                  <a
                    key={i}
                    href={l.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-hidden={i >= MARQUEE.length}
                    tabIndex={i >= MARQUEE.length ? -1 : undefined}
                    className="mr-[8px] flex h-[46px] flex-none items-center justify-center rounded-[12px] border px-[14px]"
                    style={{
                      background: l.dark ? "#15173d" : "#fff",
                      borderColor: l.dark ? "rgba(255,255,255,.12)" : "#EFE6D6",
                      boxShadow: "0 6px 16px -12px rgba(80,50,20,.4)",
                    }}
                  >
                    <img src={l.src} alt={i >= MARQUEE.length ? "" : l.alt} className="block w-auto" style={{ height: l.h }} />
                  </a>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT — scattered logos (desktop only) */}
          <div className="relative hidden h-[660px] min-w-[340px] flex-[1_1_440px] translate-y-[56px] md:block">
            {SCATTER.map((l) => (
              <a
                key={l.src}
                href={l.href}
                target="_blank"
                rel="noopener noreferrer"
                className={`fund-logo absolute flex items-center justify-center rounded-[16px] border no-underline${l.dark ? " fund-logo-dark" : ""}`}
                style={{
                  left: l.left,
                  top: l.top,
                  width: l.w,
                  padding: l.pad,
                  transform: `rotate(${l.rot}deg)`,
                  background: l.dark ? "#15173d" : "#fff",
                  borderColor: l.dark ? "rgba(255,255,255,.12)" : "#EFE6D6",
                }}
              >
                <img
                  src={l.src}
                  alt={l.alt}
                  className="block h-auto w-full"
                  style={{ pointerEvents: "none", borderRadius: l.imgRadius }}
                />
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
