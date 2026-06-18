export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-[rgba(244,238,228,.86)] [backdrop-filter:blur(12px)]">
      <div className="mx-auto flex max-w-[1240px] items-center justify-center gap-[13px] px-[28px] py-[15px]">
        <div className="flex h-[34px] w-[34px] items-center justify-center rounded-[10px] bg-clay text-[18px] font-extrabold text-white">
          П
        </div>
        <div className="text-[21px] font-bold tracking-[-.015em]">ПМО - Карта рынка агентов</div>
      </div>
    </header>
  );
}
