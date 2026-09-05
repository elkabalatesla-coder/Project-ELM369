import { useState, useRef } from "react";

const WAVESPEED_MODEL = "black-forest-labs/FLUX.1-dev";

export default function ELM369FluxGenerator() {
  const [token, setToken] = useState("");
  const [prompt, setPrompt] = useState("A cyberpunk street scene at night");
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [log, setLog] = useState([]);
  const logRef = useRef([]);

  const addLog = (msg, type = "info") => {
    const entry = {
      time: new Date().toLocaleTimeString(),
      msg,
      type,
      id: Date.now(),
    };
    logRef.current = [entry, ...logRef.current.slice(0, 19)];
    setLog([...logRef.current]);
  };

  const generate = async () => {
    if (!token.trim()) {
      setError("❌ HF_TOKEN required. Paste your Hugging Face token above.");
      return;
    }
    if (!prompt.trim()) {
      setError("❌ Prompt cannot be empty.");
      return;
    }
    setError(null);
    setImageUrl(null);
    setLoading(true);
    addLog(`🚀 Initiating generation — model: FLUX.1-dev via WaveSpeed`, "info");
    addLog(`📝 Prompt: "${prompt}"`, "info");

    try {
      const res = await fetch(
        `https://api-inference.huggingface.co/models/${WAVESPEED_MODEL}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ inputs: prompt }),
        }
      );

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`API error ${res.status}: ${errText}`);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setImageUrl(url);
      addLog("✅ Image generated successfully.", "success");
      addLog(`📦 ELM369 Security Log — output captured | JMR0824197846902`, "vault");
    } catch (err) {
      setError(`❌ ${err.message}`);
      addLog(`⚠️ Error: ${err.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const typeColor = (type) => {
    switch (type) {
      case "success": return "#00ffcc";
      case "error": return "#ff4466";
      case "vault": return "#a78bfa";
      default: return "#7dd3fc";
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#050a0f",
      color: "#e0f7ff",
      fontFamily: "'JetBrains Mono', 'Courier New', monospace",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "2rem 1rem",
    }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <div style={{
          fontSize: "0.7rem",
          letterSpacing: "0.3em",
          color: "#00e5ff",
          marginBottom: "0.4rem",
        }}>PROJECT ELM369 · JMR0824197846902</div>
        <h1 style={{
          fontSize: "clamp(1.4rem, 4vw, 2.2rem)",
          fontWeight: 700,
          margin: 0,
          background: "linear-gradient(90deg, #00e5ff, #00ffcc)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          letterSpacing: "0.05em",
        }}>FLUX IMAGE ENGINE</h1>
        <div style={{ fontSize: "0.65rem", color: "#4a7fa5", marginTop: "0.3rem", letterSpacing: "0.2em" }}>
          FLUX.1-dev · WaveSpeed Provider · AI Team Artifact
        </div>
      </div>

      {/* Main card */}
      <div style={{
        width: "100%",
        maxWidth: "680px",
        background: "#0a1520",
        border: "1px solid #0e3a52",
        borderRadius: "12px",
        padding: "1.5rem",
        boxShadow: "0 0 40px rgba(0,229,255,0.05)",
      }}>
        {/* Token input */}
        <label style={{ fontSize: "0.7rem", color: "#4a9eba", letterSpacing: "0.15em", display: "block", marginBottom: "0.4rem" }}>
          HF_TOKEN (Hugging Face API Key)
        </label>
        <input
          type="password"
          value={token}
          onChange={e => setToken(e.target.value)}
          placeholder="hf_xxxxxxxxxxxxxxxxxxxxxxxxxx"
          style={{
            width: "100%",
            background: "#071018",
            border: "1px solid #0e3a52",
            borderRadius: "6px",
            padding: "0.65rem 0.9rem",
            color: "#00e5ff",
            fontSize: "0.8rem",
            fontFamily: "inherit",
            outline: "none",
            boxSizing: "border-box",
            marginBottom: "1rem",
          }}
        />

        {/* Prompt input */}
        <label style={{ fontSize: "0.7rem", color: "#4a9eba", letterSpacing: "0.15em", display: "block", marginBottom: "0.4rem" }}>
          PROMPT
        </label>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          rows={3}
          style={{
            width: "100%",
            background: "#071018",
            border: "1px solid #0e3a52",
            borderRadius: "6px",
            padding: "0.65rem 0.9rem",
            color: "#e0f7ff",
            fontSize: "0.85rem",
            fontFamily: "inherit",
            outline: "none",
            resize: "vertical",
            boxSizing: "border-box",
            marginBottom: "1.2rem",
          }}
        />

        {/* Generate button */}
        <button
          onClick={generate}
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.85rem",
            background: loading ? "#0a2030" : "linear-gradient(90deg, #006e8a, #00c9b0)",
            border: "none",
            borderRadius: "8px",
            color: "#fff",
            fontSize: "0.85rem",
            fontFamily: "inherit",
            letterSpacing: "0.15em",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: 700,
            transition: "opacity 0.2s",
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? "⟳ GENERATING..." : "▶ GENERATE IMAGE"}
        </button>

        {/* Error */}
        {error && (
          <div style={{
            marginTop: "1rem",
            padding: "0.75rem",
            background: "#1a0a0f",
            border: "1px solid #ff4466",
            borderRadius: "6px",
            color: "#ff6688",
            fontSize: "0.78rem",
          }}>{error}</div>
        )}

        {/* Image output */}
        {imageUrl && (
          <div style={{ marginTop: "1.5rem", textAlign: "center" }}>
            <div style={{ fontSize: "0.65rem", color: "#4a9eba", letterSpacing: "0.2em", marginBottom: "0.6rem" }}>
              OUTPUT · PANDORA VAULT READY
            </div>
            <img
              src={imageUrl}
              alt="Generated"
              style={{
                width: "100%",
                borderRadius: "8px",
                border: "1px solid #0e3a52",
                boxShadow: "0 0 30px rgba(0,229,255,0.1)",
              }}
            />
            <a
              href={imageUrl}
              download="ELM369_flux_output.png"
              style={{
                display: "inline-block",
                marginTop: "0.8rem",
                padding: "0.5rem 1.2rem",
                background: "#071018",
                border: "1px solid #00e5ff",
                borderRadius: "6px",
                color: "#00e5ff",
                fontSize: "0.75rem",
                textDecoration: "none",
                letterSpacing: "0.1em",
              }}
            >⬇ DOWNLOAD IMAGE</a>
          </div>
        )}
      </div>

      {/* Security / Activity Log */}
      <div style={{
        width: "100%",
        maxWidth: "680px",
        marginTop: "1.5rem",
        background: "#060d14",
        border: "1px solid #0a2535",
        borderRadius: "10px",
        padding: "1rem 1.2rem",
      }}>
        <div style={{ fontSize: "0.65rem", color: "#4a9eba", letterSpacing: "0.2em", marginBottom: "0.7rem" }}>
          ELM369 SECURITY LOG · PANDORA VAULT FEED
        </div>
        {log.length === 0 && (
          <div style={{ color: "#2a5a70", fontSize: "0.75rem" }}>Awaiting activity...</div>
        )}
        {log.map(entry => (
          <div key={entry.id} style={{
            display: "flex",
            gap: "0.8rem",
            fontSize: "0.72rem",
            marginBottom: "0.35rem",
            borderBottom: "1px solid #0a1f2e",
            paddingBottom: "0.3rem",
          }}>
            <span style={{ color: "#2a5a70", minWidth: "60px" }}>{entry.time}</span>
            <span style={{ color: typeColor(entry.type) }}>{entry.msg}</span>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "1.5rem", fontSize: "0.6rem", color: "#1a3a4a", letterSpacing: "0.15em", textAlign: "center" }}>
        ELM369 · JMR0824197846902 · 1550e4d5-9ee3-49cd-8af8-7c9d630f84ad · AI TEAM ARTIFACT
      </div>
    </div>
  );
}
