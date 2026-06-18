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
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        background: "rgba(40,28,18,.46)",
        backdropFilter: "blur(3px)",
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "center",
        padding: "5vh 16px",
        overflowY: "auto",
        animation: "fadeIn .2s both",
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={agent.name}
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(720px,100%)",
          background: C.cardAlt,
          borderRadius: 22,
          border: `1px solid ${C.border}`,
          boxShadow: "0 30px 80px -30px rgba(60,40,20,.6)",
          overflow: "hidden",
          animation: "fadeUp .26s both",
        }}
      >
        {/* header */}
        <div style={{ padding: "24px 30px 20px", background: C.card, borderBottom: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, marginBottom: 14 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 9, flexWrap: "wrap" }}>
              <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".03em", color: C.faint }}>{agent.category}</span>
              <StatusBadge label={sm.label} color={sm.color} bg={sm.bg} small />
            </div>
            <button
              onClick={onClose}
              aria-label="Закрыть"
              style={{ cursor: "pointer", border: `1px solid ${C.border}`, background: "#fff", borderRadius: "50%", width: 34, height: 34, fontSize: 17, color: C.muted, display: "flex", alignItems: "center", justifyContent: "center", flex: "none" }}
            >
              ✕
            </button>
          </div>
          <h2 style={{ fontFamily: FONT_SERIF, fontWeight: 400, fontSize: 28, letterSpacing: "-.015em", margin: "0 0 8px", lineHeight: 1.1 }}>{agent.name}</h2>
          {agent.role && <p style={{ margin: 0, fontSize: 14.5, lineHeight: 1.5, color: "#6B5E4D" }}>{agent.role}</p>}
          {agent.resourceLink && (
            <a href={agent.resourceLink} target="_blank" rel="noreferrer" style={{ display: "inline-block", marginTop: 14, fontSize: 12.5, fontWeight: 700, color: C.clay, textDecoration: "none" }}>
              Открыть прототип агента →
            </a>
          )}
        </div>

        {/* body */}
        <div style={{ padding: "8px 30px 30px" }}>
          {agent.userStory && (
            <Section title="Пользовательская история">
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.55, color: "#6B5E4D", fontStyle: "italic", borderLeft: `2px solid ${C.clay}`, paddingLeft: 13 }}>
                «{agent.userStory}»
              </p>
            </Section>
          )}

          {agent.functionalRequirements.length > 0 && (
            <Section title="Функциональные требования">
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13.5, lineHeight: 1.6, color: C.inkSoft }}>
                {agent.functionalRequirements.map((fr, i) => (
                  <li key={i} style={{ marginBottom: 4 }}>{fr}</li>
                ))}
              </ul>
            </Section>
          )}

          {agent.expectedBehavior && (
            <Section title="Ожидаемое поведение">
              <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: C.inkSoft }}>{agent.expectedBehavior}</p>
            </Section>
          )}

          {(agent.inputs || agent.outputs) && (
            <Section title="Входы и выходы">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                {agent.inputs && <IOCard label="Входы" text={agent.inputs} />}
                {agent.outputs && <IOCard label="Выходы" text={agent.outputs} />}
              </div>
            </Section>
          )}

          {(agent.cjmClassroom || agent.cjmPlatform) && (
            <Section title="Сценарии использования">
              <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 10 }}>
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
    <div style={{ paddingTop: 18 }}>
      <div style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".03em", color: C.faint, marginBottom: 10 }}>{title}</div>
      {children}
    </div>
  );
}

function IOCard({ label, text }: { label: string; text: string }) {
  return (
    <div style={{ background: "#fff", border: `1px solid ${C.borderWarm}`, borderRadius: 12, padding: "12px 14px" }}>
      <div style={{ fontSize: 10.5, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".04em", color: C.faint, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 13, lineHeight: 1.5, color: C.inkSoft }}>{text}</div>
    </div>
  );
}

function CjmCard({ label, text, accent }: { label: string; text: string; accent?: boolean }) {
  return (
    <div style={{ background: accent ? "#E7F0EC" : "#fff", border: `1px solid ${accent ? "#CFE2DA" : C.borderWarm}`, borderRadius: 13, padding: "13px 16px" }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: accent ? C.teal : "#9A6A4A", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 13, lineHeight: 1.55, color: C.inkSoft }}>{text}</div>
    </div>
  );
}
