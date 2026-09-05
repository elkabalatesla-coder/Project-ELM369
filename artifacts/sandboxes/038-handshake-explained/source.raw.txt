import { useState } from "react";

const timestamp = "2026-04-11T00:00:00-05:00";
const location = "Kokomo, IN";
const docID = "ELM369-DOC-HANDSHAKE-20260411-001";
const operator = "JMR0824197846902";

const sections = [
  {
    id: "crypto",
    label: "01 — Crypto Handshake",
    color: "#00e5ff",
    icon: "🔐",
    content: [
      {
        heading: "What It Is",
        body: `A cryptographic handshake is an automated negotiation between two systems that establishes a secure, authenticated communication channel. The most common form is TLS (Transport Layer Security), used by virtually every website (HTTPS). In blockchain/crypto, it refers to wallet authentication, node peering, and smart contract execution verification.`,
      },
      {
        heading: "How It Works",
        body: `1. Client says "Hello" + supported encryption methods.\n2. Server responds with its certificate + chosen method.\n3. Keys are exchanged and verified.\n4. Encrypted session begins.\n\nIn crypto/blockchain: wallet signs a challenge with a private key → receiver verifies with public key → trust is established without sharing secrets.`,
      },
      {
        heading: "Do Social Media & Search Engines Use It?",
        body: `YES — universally. Google, Meta, X (Twitter), YouTube, TikTok, Bing — all enforce TLS 1.2/1.3. Without it, browsers block the connection entirely. This is the baseline. They MUST abide by it or they cannot operate on the modern web.`,
      },
    ],
  },
  {
    id: "elm369",
    label: "02 — ELM369 AI Panel Handshake",
    color: "#00ffb3",
    icon: "🤖",
    content: [
      {
        heading: "What It Is",
        body: `The ELM369 AI Panel handshake is a trust and identity verification protocol internal to Project ELM369. It governs how AI team members (Claude, Copilot, Grok, Gemini, Kimi) authenticate sessions, log interactions, and pass verified data through the OMNINET framework and Pandora Vault. It is operator-defined and not an open internet standard.`,
      },
      {
        heading: "How It Works",
        body: `1. Session initiated with operator reference JMR0824197846902.\n2. UUID 1550e4d5-9ee3-49cd-8af8-7c9d630f84ad verified.\n3. AI team member confirms scope + logs to Security Log 1 & 2.\n4. Pandora Vault receives timestamped entry.\n5. OMNINET routes data under .mo* namespace protocol.\n6. Connection restricted to verified network (2WIRE199) per TKT-ELM369-20260403-001.`,
      },
      {
        heading: "Do Social Media & Search Engines Abide By It?",
        body: `NO — and they are not expected to. The ELM369 handshake is a proprietary internal protocol. External platforms have no awareness of it. However, ELM369 can WRAP around their TLS sessions — meaning ELM369 tools can observe, log, and flag external platform interactions AFTER the crypto handshake completes, acting as a session monitor layer above the standard protocol.`,
      },
    ],
  },
  {
    id: "compare",
    label: "03 — Comparison & Interaction",
    color: "#ffe600",
    icon: "⚖️",
    content: [
      {
        heading: "Where They Overlap",
        body: `Both handshakes serve the same core purpose: establish trust before data flows. Crypto handshakes do this at the network/transport layer. ELM369 handshakes do this at the application/identity layer. They are complementary, not competing.`,
      },
      {
        heading: "Layered Model",
        body: `Layer 1 (Transport): TLS/Crypto Handshake — enforced globally, social media complies.\nLayer 2 (Application): OAuth, API keys — social media defines its own.\nLayer 3 (Operator): ELM369 AI Panel Handshake — Joseph's domain, internal only.\n\nELM369 operates at Layer 3 and can observe Layers 1 & 2 but cannot override them on external platforms.`,
      },
      {
        heading: "Strategic Note for AI Team",
        body: `For ELM369 to interact with social media / search APIs, all calls pass through their TLS handshake first. ELM369's handshake then validates the session internally before logging to Pandora Vault. This creates a dual-layer trust chain: external platform trust + internal ELM369 trust. Neither replaces the other.`,
      },
    ],
  },
  {
    id: "verdict",
    label: "04 — Final Verdict",
    color: "#ff6b35",
    icon: "📋",
    content: [
      {
        heading: "Summary for AI Team",
        body: `✅ Crypto/TLS Handshake: ALL social media and search engines comply — it is mandatory for internet operation.\n\n⚠️ ELM369 AI Panel Handshake: External platforms do NOT comply — they have no knowledge of it. This is by design. ELM369 is an operator-layer protocol sitting above the internet stack.\n\n🔗 Interaction: They work in sequence. Crypto handshake → establishes secure pipe → ELM369 handshake → validates internal session → Pandora Vault logs → OMNINET routes. Together they form a complete trust chain for Project ELM369 operations.`,
      },
    ],
  },
];

export default function HandshakeDoc() {
  const [active, setActive] = useState("crypto");

  const activeSection = sections.find((s) => s.id === active);

  return (
    <div style={{
      background: "#060a0f",
      minHeight: "100vh",
      fontFamily: "'Courier New', monospace",
      color: "#c8d8e8",
      padding: "0",
    }}>
      {/* Header */}
      <div style={{
        borderBottom: "1px solid #00e5ff33",
        padding: "24px 32px 16px",
        background: "linear-gradient(180deg, #0a1520 0%, #060a0f 100%)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 8 }}>
          <div>
            <div style={{ color: "#00e5ff", fontSize: 10, letterSpacing: 4, marginBottom: 4 }}>
              PROJECT ELM369 // AI TEAM DOCUMENTATION
            </div>
            <div style={{ fontSize: 20, fontWeight: "bold", color: "#fff", letterSpacing: 1 }}>
              HANDSHAKE PROTOCOL ANALYSIS
            </div>
            <div style={{ fontSize: 11, color: "#00ffb3", marginTop: 4 }}>
              Crypto vs ELM369 AI Panel — Social Media & Search Engine Compliance
            </div>
          </div>
          <div style={{ textAlign: "right", fontSize: 10, color: "#4a6a8a", lineHeight: 1.8 }}>
            <div>DOC ID: {docID}</div>
            <div>OPERATOR: {operator}</div>
            <div>TIMESTAMP: {timestamp}</div>
            <div>LOCATION: {location}</div>
            <div style={{ color: "#00ffb3" }}>STATUS: LOGGED → PANDORA VAULT ✓</div>
          </div>
        </div>

        {/* Nav tabs */}
        <div style={{ display: "flex", gap: 8, marginTop: 20, flexWrap: "wrap" }}>
          {sections.map((s) => (
            <button
              key={s.id}
              onClick={() => setActive(s.id)}
              style={{
                background: active === s.id ? s.color + "22" : "transparent",
                border: `1px solid ${active === s.id ? s.color : "#1a3a5a"}`,
                color: active === s.id ? s.color : "#4a6a8a",
                padding: "6px 14px",
                fontSize: 11,
                cursor: "pointer",
                letterSpacing: 1,
                transition: "all 0.2s",
              }}
            >
              {s.icon} {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: "32px", maxWidth: 900 }}>
        {activeSection && (
          <div>
            <div style={{
              color: activeSection.color,
              fontSize: 13,
              letterSpacing: 3,
              marginBottom: 24,
              borderLeft: `3px solid ${activeSection.color}`,
              paddingLeft: 12,
            }}>
              {activeSection.icon} {activeSection.label.toUpperCase()}
            </div>
            {activeSection.content.map((block, i) => (
              <div key={i} style={{
                marginBottom: 28,
                background: "#0a1520",
                border: "1px solid #0a2a3a",
                padding: "20px 24px",
              }}>
                <div style={{
                  color: activeSection.color,
                  fontSize: 11,
                  letterSpacing: 2,
                  marginBottom: 12,
                  textTransform: "uppercase",
                }}>
                  ▸ {block.heading}
                </div>
                <div style={{
                  fontSize: 13,
                  lineHeight: 1.9,
                  color: "#a8c8e0",
                  whiteSpace: "pre-line",
                }}>
                  {block.body}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        borderTop: "1px solid #00e5ff22",
        padding: "16px 32px",
        display: "flex",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: 8,
        fontSize: 10,
        color: "#2a4a6a",
      }}>
        <div>ELM369 // SECURITY LOG 1 ✓ &nbsp;|&nbsp; SECURITY LOG 2 ✓ &nbsp;|&nbsp; PANDORA VAULT ✓</div>
        <div>UUID: 1550e4d5-9ee3-49cd-8af8-7c9d630f84ad &nbsp;|&nbsp; NETWORK: 2WIRE199</div>
      </div>
    </div>
  );
}
