/** Sticky top bar — transparent at rest, frosted once the page scrolls. */
export default function Header({ scrolled }: { scrolled: boolean }) {
  return (
    <header
      className="sticky top-0 z-50 transition-[background-color,backdrop-filter] duration-[250ms]"
      style={{
        background: scrolled ? "rgba(244,238,228,.82)" : "transparent",
        backdropFilter: scrolled ? "blur(14px)" : "blur(0px)",
        WebkitBackdropFilter: scrolled ? "blur(14px)" : "blur(0px)",
      }}
    >
      <div className="mx-auto flex max-w-[1240px] items-center justify-center gap-[9px] px-[18px] py-[12px] md:gap-[13px] md:px-[28px] md:py-[15px]">
        <div className="flex h-[26px] w-[26px] flex-none items-center justify-center rounded-[8px] bg-clay text-[14px] font-extrabold text-white md:h-[34px] md:w-[34px] md:rounded-[10px] md:text-[18px]">
          п
        </div>
        <div className="font-bold tracking-[-.01em] text-[15.5px] md:text-[21px] md:tracking-[-.015em]">
          <span className="md:hidden">ПМО — Лучшие практики</span>
          <span className="hidden md:inline">ПМО — Лучшие мировые практики</span>
        </div>
      </div>
    </header>
  );
}
