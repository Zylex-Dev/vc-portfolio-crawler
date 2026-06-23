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
        <svg viewBox="0 0 24 24" className="h-[28px] w-[28px] flex-none md:h-[36px] md:w-[36px]" fill="none" stroke="#C2603C" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <path d="M20 7H17.8486C17.3511 7 17 6.49751 17 6C17 4.34315 15.6569 3 14 3C12.3431 3 11 4.34315 11 6C11 6.49751 10.6488 7 10.1513 7H8C7.44771 7 7 7.44772 7 8V10.1513C7 10.6488 6.49751 11 6 11C4.34315 11 3 12.3431 3 14C3 15.6569 4.34315 17 6 17C6.49751 17 7 17.3511 7 17.8486V20C7 20.5523 7.44771 21 8 21L20 21C20.5523 21 21 20.5523 21 20V17.8486C21 17.3511 20.4975 17 20 17C18.3431 17 17 15.6569 17 14C17 12.3431 18.3431 11 20 11C20.4975 11 21 10.6488 21 10.1513L21 8C21 7.44772 20.5523 7 20 7Z" />
        </svg>
        <div className="font-bold tracking-[-.01em] text-[15.5px] md:text-[21px] md:tracking-[-.015em]">
          <span className="md:hidden">ПМО — Лучшие практики</span>
          <span className="hidden md:inline">ПМО — Лучшие мировые практики</span>
        </div>
      </div>
    </header>
  );
}
