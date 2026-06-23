import { useEffect } from "react";
import type { Agent } from "../types";
import { C, FONT_SERIF, statusMeta } from "../theme";
import { StatusBadge } from "./shared";

/** Full per-agent detail, opened from the drawer's agent title. */
export default function AgentModal({ agent, onClose }: { agent: Agent | null; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!agent) return null;
  const sm = statusMeta(agent.status);

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-[100] flex items-start justify-center overflow-y-auto bg-[rgba(40,28,18,.46)] px-[16px] py-[5vh] [backdrop-filter:blur(3px)]"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={agent.name}
        onClick={(e) => e.stopPropagation()}
        className="w-[min(720px,100%)] overflow-hidden rounded-[22px] border border-border bg-card-alt [box-shadow:0_30px_80px_-30px_rgba(60,40,20,.6)]"
      >
        {/* header */}
        <div className="border-b border-border bg-card px-[30px] pb-[20px] pt-[24px]">
          <div className="mb-[14px] flex items-center justify-between gap-[12px]">
            <div className="flex flex-wrap items-center gap-[9px]">
              <span className="text-[11px] font-bold uppercase tracking-[.03em] text-faint">{agent.category}</span>
              <StatusBadge label={sm.label} color={sm.color} bg={sm.bg} small />
            </div>
            <button
              onClick={onClose}
              aria-label="Закрыть"
              className="flex h-[34px] w-[34px] flex-none cursor-pointer items-center justify-center rounded-full border border-border bg-white text-[17px] text-muted"
            >
              ✕
            </button>
          </div>
          <h2
            className="m-0 mb-[8px] text-[28px] font-normal leading-[1.1] tracking-[-.015em]"
            style={{ fontFamily: FONT_SERIF }}
          >
            {agent.name}
          </h2>
          {agent.role && <p className="m-0 text-[14.5px] leading-[1.5] text-prose">{agent.role}</p>}
          {agent.resourceLink && (
            <a
              href={agent.resourceLink}
              target="_blank"
              rel="noreferrer"
              className="mt-[14px] inline-block text-[12.5px] font-bold text-clay no-underline"
            >
              Открыть прототип агента →
            </a>
          )}
        </div>

        {/* body */}
        <div className="px-[30px] pb-[30px] pt-[8px]">
          {agent.userStory && (
            <Section title="Пользовательская история">
              <p className="m-0 border-l-2 border-clay pl-[13px] text-[14px] italic leading-[1.55] text-prose">
                «{agent.userStory}»
              </p>
            </Section>
          )}

          {agent.functionalRequirements.length > 0 && (
            <Section title="Функциональные требования">
              <ul className="m-0 pl-[18px] text-[13.5px] leading-[1.6] text-ink-soft">
                {agent.functionalRequirements.map((fr, i) => (
                  <li key={i} className="mb-[4px]">{fr}</li>
                ))}
              </ul>
            </Section>
          )}

          {agent.expectedBehavior && (
            <Section title="Ожидаемое поведение">
              <p className="m-0 text-[13.5px] leading-[1.6] text-ink-soft">{agent.expectedBehavior}</p>
            </Section>
          )}

          {(agent.inputs || agent.outputs) && (
            <Section title="Входы и выходы">
              <div className="grid grid-cols-2 gap-[10px]">
                {agent.inputs && <IOCard label="Входы" text={agent.inputs} />}
                {agent.outputs && <IOCard label="Выходы" text={agent.outputs} />}
              </div>
            </Section>
          )}

          {(agent.cjmClassroom || agent.cjmPlatform) && (
            <Section title="Сценарии использования">
              <div className="grid grid-cols-1 gap-[10px]">
                {agent.cjmClassroom && <CjmCard label="В классе – без платформы" text={agent.cjmClassroom} />}
                {agent.cjmPlatform && <CjmCard label="На платформе" text={agent.cjmPlatform} accent />}
              </div>
            </Section>
          )}
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="pt-[18px]">
      <div className="mb-[10px] text-[11px] font-bold uppercase tracking-[.03em] text-faint">{title}</div>
      {children}
    </div>
  );
}

function IOCard({ label, text }: { label: string; text: string }) {
  return (
    <div className="rounded-[12px] border border-border-warm bg-white px-[14px] py-[12px]">
      <div className="mb-[6px] text-[10.5px] font-bold uppercase tracking-[.04em] text-faint">{label}</div>
      <div className="text-[13px] leading-[1.5] text-ink-soft">{text}</div>
    </div>
  );
}

function CjmCard({ label, text, accent }: { label: string; text: string; accent?: boolean }) {
  return (
    <div
      className="rounded-[13px] border px-[16px] py-[13px]"
      style={{ background: accent ? "#E7F0EC" : "#fff", borderColor: accent ? "#CFE2DA" : C.borderWarm }}
    >
      <div
        className="mb-[6px] text-[11px] font-bold"
        style={{ color: accent ? C.teal : "#9A6A4A" }}
      >
        {label}
      </div>
      <div className="text-[13px] leading-[1.55] text-ink-soft">{text}</div>
    </div>
  );
}
