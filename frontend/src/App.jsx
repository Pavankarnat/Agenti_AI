import { useState, useRef, useCallback } from "react";

// ── Constants ──────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:8000";

const AGENTS = [
  { id: "planner",    name: "Planner",    file: "planner.py",    icon: "◈", color: "#00FFB2", desc: "Decomposes your goal into targeted search queries" },
  { id: "websearch",  name: "Web Search", file: "web_search.py", icon: "⬢", color: "#38BDF8", desc: "Runs DuckDuckGo queries, deduplicates and ranks URLs" },
  { id: "researcher", name: "Researcher", file: "researcher.py", icon: "⬡", color: "#FF6B35", desc: "Scrapes & extracts content from the top URLs" },
  { id: "writer",     name: "Writer",     file: "writer.py",     icon: "◇", color: "#A78BFA", desc: "Synthesises a structured research brief via LLM" },
];
const PIPELINE = ["planner", "websearch", "researcher", "writer"];

// ── Sub-components ─────────────────────────────────────────────────────────

function TerminalLog({ logs, color }) {
  const endRef = useRef(null);
  // auto-scroll
  const prev = useRef(0);
  if (logs.length !== prev.current) {
    prev.current = logs.length;
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }
  return (
    <div style={{
      background: "#020810", border: `1px solid ${color}18`, borderRadius: 8,
      padding: "14px 16px", fontFamily: "'Courier New', monospace", fontSize: 11,
      height: 170, overflowY: "auto",
    }}>
      <div style={{ color: "#1F2937", marginBottom: 8, letterSpacing: "0.14em", fontSize: 10 }}>
        ── LIVE OUTPUT ──────────────────────────────
      </div>
      {logs.length === 0
        ? <div style={{ color: "#1F2937" }}>Awaiting activation…</div>
        : logs.map((line, i) => (
            <div key={i} style={{ color: color, opacity: 0.82, marginBottom: 3, animation: "fadeIn .25s ease" }}>
              <span style={{ color: "#374151", marginRight: 8 }}>›</span>{line}
            </div>
          ))
      }
      <div ref={endRef} />
    </div>
  );
}

function StatusBadge({ state, color }) {
  const cfg = {
    idle:    { label: "IDLE",    dot: "#374151", bg: "#111827", border: "#1F2937" },
    running: { label: "RUNNING", dot: color,     bg: `${color}18`, border: `${color}55`, blink: true },
    done:    { label: "DONE",    dot: "#22c55e", bg: "#05140c", border: "#22c55e44" },
    error:   { label: "ERROR",   dot: "#ef4444", bg: "#150505", border: "#ef444444" },
  }[state] || {};
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 5, padding: "3px 10px",
      borderRadius: 20, background: cfg.bg, border: `1px solid ${cfg.border}`,
    }}>
      <div style={{
        width: 6, height: 6, borderRadius: "50%", background: cfg.dot,
        animation: cfg.blink ? "blink 1s infinite" : "none",
      }} />
      <span style={{
        fontSize: 10, fontFamily: "'Courier New', monospace",
        color: state === "running" ? color : state === "done" ? "#22c55e" : "#4B5563",
        letterSpacing: "0.08em",
      }}>{cfg.label}</span>
    </div>
  );
}

function AgentCard({ agent, state, logs, data }) {
  const isRunning = state === "running";
  return (
    <div style={{
      background: isRunning ? `linear-gradient(135deg,#0A0F1A,${agent.color}08)` : "#080C14",
      border: `1px solid ${state !== "idle" ? agent.color + (state === "done" ? "44" : "99") : "#1F2937"}`,
      borderRadius: 12, padding: 22, transition: "all .4s ease", position: "relative", overflow: "hidden",
      boxShadow: isRunning ? `0 0 28px ${agent.color}18` : "none",
    }}>
      {/* corner glow */}
      <div style={{
        position: "absolute", top: 0, right: 0, width: 56, height: 56,
        background: `linear-gradient(225deg,${agent.color}12,transparent 60%)`,
        borderRadius: "0 12px 0 56px",
      }} />

      {/* header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 11 }}>
          <div style={{
            fontSize: 26, color: agent.color,
            filter: isRunning ? `drop-shadow(0 0 7px ${agent.color})` : "none",
            animation: isRunning ? "iconPulse 1.6s ease-in-out infinite" : "none",
          }}>{agent.icon}</div>
          <div>
            <div style={{ fontFamily: "'Space Mono',monospace", fontSize: 15, fontWeight: 700, color: "#F9FAFB", letterSpacing: ".05em" }}>
              {agent.name}
            </div>
            <div style={{ fontSize: 10, color: "#4B5563", fontFamily: "'Courier New',monospace", letterSpacing: ".1em" }}>
              {agent.file}
            </div>
          </div>
        </div>
        <StatusBadge state={state} color={agent.color} />
      </div>

      <p style={{ color: "#6B7280", fontSize: 12, marginBottom: 14, lineHeight: 1.55 }}>{agent.desc}</p>
      <TerminalLog logs={logs} color={agent.color} />

      {/* metadata pills when done */}
      {state === "done" && data && (
        <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 6 }}>
          {agent.id === "planner" && data.search_queries?.map((q, i) => (
            <span key={i} style={pill(agent.color)}>Q{i + 1}: {q.slice(0, 40)}{q.length > 40 ? "…" : ""}</span>
          ))}
          {agent.id === "websearch" && (
            <span style={pill(agent.color)}>{data.total_results} URLs found</span>
          )}
          {agent.id === "researcher" && data.sources?.map((s, i) => (
            <span key={i} style={pill(agent.color)}>
              {s.status === "success" ? "✓" : "✗"} {s.words} words
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

const pill = (color) => ({
  fontSize: 10, padding: "3px 9px", borderRadius: 20,
  background: `${color}12`, border: `1px solid ${color}33`,
  color: color, fontFamily: "'Courier New',monospace", letterSpacing: ".06em",
  maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
});

function PipelineBar({ agentStates }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", padding: "18px 28px",
      background: "#080C14", border: "1px solid #1F2937", borderRadius: 12,
      marginBottom: 28, position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(90deg,#00FFB206,transparent 50%)", pointerEvents: "none" }} />
      {PIPELINE.map((id, i) => {
        const agent = AGENTS.find(a => a.id === id);
        const st = agentStates[id];
        const isActive = st === "running";
        const isDone   = st === "done";
        return (
          <div key={id} style={{ display: "flex", alignItems: "center", flex: 1 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 7, flex: 1 }}>
              <div style={{
                width: 38, height: 38, borderRadius: "50%",
                border: `2px solid ${isActive ? agent.color : isDone ? agent.color + "77" : "#1F2937"}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 17, color: isActive ? agent.color : isDone ? agent.color + "88" : "#374151",
                background: isActive ? `${agent.color}15` : "transparent",
                boxShadow: isActive ? `0 0 14px ${agent.color}44` : "none",
                transition: "all .4s ease",
              }}>
                {isDone && !isActive ? "✓" : agent.icon}
              </div>
              <span style={{
                fontSize: 9, fontFamily: "'Courier New',monospace", letterSpacing: ".12em",
                color: isActive ? agent.color : isDone ? agent.color + "88" : "#374151",
              }}>{agent.name.toUpperCase()}</span>
            </div>
            {i < PIPELINE.length - 1 && (
              <div style={{
                height: 1, width: 36, flexShrink: 0,
                background: isDone
                  ? `linear-gradient(90deg,${agent.color}55,${AGENTS.find(a => a.id === PIPELINE[i + 1]).color}33)`
                  : "#1F2937",
                transition: "all .5s ease",
              }} />
            )}
          </div>
        );
      })}
    </div>
  );
}

function ResultPanel({ result }) {
  const [tab, setTab] = useState("summary");
  if (!result) return null;

  return (
    <div style={{
      background: "#080C14", border: "1px solid #22c55e33", borderRadius: 12,
      padding: 26, marginTop: 24, animation: "fadeIn .5s ease",
      position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 1, background: "linear-gradient(90deg,transparent,#22c55e55,transparent)" }} />

      {/* header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <div style={{ color: "#22c55e", fontSize: 20 }}>◈</div>
        <div>
          <div style={{ fontFamily: "'Space Mono',monospace", fontSize: 14, fontWeight: 700, color: "#22c55e", letterSpacing: ".05em" }}>
            PIPELINE COMPLETE
          </div>
          <div style={{ fontSize: 11, color: "#4B5563", fontFamily: "'Courier New',monospace", letterSpacing: ".1em" }}>
            {result.title}
          </div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 11, color: "#22c55e", fontFamily: "'Courier New',monospace" }}>
            Confidence: {(result.confidence_score * 100).toFixed(0)}%
          </span>
          <div style={{
            width: 80, height: 4, background: "#1F2937", borderRadius: 2, overflow: "hidden",
          }}>
            <div style={{
              height: "100%", borderRadius: 2,
              width: `${result.confidence_score * 100}%`,
              background: "linear-gradient(90deg,#22c55e,#38BDF8)",
              transition: "width 1s ease",
            }} />
          </div>
        </div>
      </div>

      {/* tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
        {["summary", "findings", "sources", "markdown"].map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: "6px 14px", borderRadius: 6, fontSize: 11, cursor: "pointer",
            fontFamily: "'Courier New',monospace", letterSpacing: ".1em",
            background: tab === t ? "#22c55e18" : "transparent",
            border: `1px solid ${tab === t ? "#22c55e55" : "#1F2937"}`,
            color: tab === t ? "#22c55e" : "#4B5563",
            transition: "all .2s ease",
          }}>{t.toUpperCase()}</button>
        ))}
      </div>

      {/* tab content */}
      <div style={{
        background: "#020810", border: "1px solid #1F2937", borderRadius: 8,
        padding: 20, fontFamily: "'Courier New',monospace", fontSize: 12,
        lineHeight: 1.8, color: "#9CA3AF", maxHeight: 340, overflowY: "auto",
      }}>
        {tab === "summary" && (
          <div>
            <div style={{ color: "#38BDF8", marginBottom: 8 }}>QUERY: <span style={{ color: "#9CA3AF" }}>{result.query}</span></div>
            <div style={{ color: "#38BDF8", marginBottom: 12 }}>GENERATED: <span style={{ color: "#9CA3AF" }}>{result.generation_date}</span></div>
            <div style={{ color: "#F9FAFB", lineHeight: 1.9 }}>{result.executive_summary}</div>
          </div>
        )}
        {tab === "findings" && (
          <div>
            {result.key_findings?.map((f, i) => (
              <div key={i} style={{ marginBottom: 14, paddingBottom: 14, borderBottom: "1px solid #1F2937" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ color: "#A78BFA", fontSize: 10, letterSpacing: ".1em" }}>[{f.type?.toUpperCase()}]</span>
                  <span style={{ color: "#374151", fontSize: 10 }}>relevance {(f.relevance * 100).toFixed(0)}%</span>
                </div>
                <div style={{ color: "#D1D5DB" }}>{f.finding}</div>
              </div>
            ))}
          </div>
        )}
        {tab === "sources" && (
          <div>
            {result.sources?.map((url, i) => (
              <div key={i} style={{ marginBottom: 8 }}>
                <span style={{ color: "#374151", marginRight: 8 }}>{i + 1}.</span>
                <a href={url} target="_blank" rel="noreferrer" style={{ color: "#38BDF8", textDecoration: "none" }}>
                  {url.length > 90 ? url.slice(0, 90) + "…" : url}
                </a>
              </div>
            ))}
          </div>
        )}
        {tab === "markdown" && (
          <pre style={{ whiteSpace: "pre-wrap", color: "#9CA3AF", fontSize: 11 }}>
            {result.markdown}
          </pre>
        )}
      </div>
    </div>
  );
}

// ── Main Dashboard ─────────────────────────────────────────────────────────
export default function Dashboard() {
  const [query, setQuery]           = useState("");
  const [running, setRunning]       = useState(false);
  const [agentStates, setAgentStates] = useState({ planner: "idle", websearch: "idle", researcher: "idle", writer: "idle" });
  const [agentLogs,   setAgentLogs]   = useState({ planner: [], websearch: [], researcher: [], writer: [] });
  const [agentData,   setAgentData]   = useState({ planner: null, websearch: null, researcher: null, writer: null });
  const [result,      setResult]      = useState(null);
  const [error,       setError]       = useState(null);
  const abortRef = useRef(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setRunning(false);
    setAgentStates({ planner: "idle", websearch: "idle", researcher: "idle", writer: "idle" });
    setAgentLogs({   planner: [], websearch: [], researcher: [], writer: [] });
    setAgentData({   planner: null, websearch: null, researcher: null, writer: null });
    setResult(null);
    setError(null);
  }, []);

  const runPipeline = useCallback(async () => {
    if (!query.trim() || running) return;
    reset();
    setRunning(true);
    setError(null);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`${API_BASE}/api/research/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || `HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop(); // keep incomplete chunk

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;
          try {
            const event = JSON.parse(line.slice(5).trim());
            handleEvent(event);
          } catch (_) {}
        }
      }
    } catch (e) {
      if (e.name !== "AbortError") {
        setError(e.message);
      }
    } finally {
      setRunning(false);
    }
  }, [query, running, reset]);

  const handleEvent = (event) => {
    const { agent, type, message, data } = event;

    if (type === "log" && PIPELINE.includes(agent)) {
      setAgentLogs(prev => ({ ...prev, [agent]: [...prev[agent], message] }));
    }

    if (type === "status") {
      const st = message === "RUNNING" ? "running" : message === "DONE" ? "done" : "idle";
      setAgentStates(prev => ({ ...prev, [agent]: st }));
      if (data) setAgentData(prev => ({ ...prev, [agent]: data }));
    }

    if (type === "result") {
      setResult(data);
    }

    if (type === "error") {
      setError(message);
      setRunning(false);
    }
  };

  const completedCount = Object.values(agentStates).filter(s => s === "done").length;
  const activeCount    = Object.values(agentStates).filter(s => s === "running").length;

  return (
    <div style={{ minHeight: "100vh", background: "#030712", color: "#F9FAFB", fontFamily: "'Segoe UI',sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #111827; }
        ::-webkit-scrollbar-thumb { background: #374151; border-radius: 2px; }
        @keyframes blink      { 0%,100%{opacity:1} 50%{opacity:.2} }
        @keyframes iconPulse  { 0%,100%{transform:scale(1)} 50%{transform:scale(1.14)} }
        @keyframes fadeIn     { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
        @keyframes shimmer    { 0%{background-position:-200% center} 100%{background-position:200% center} }
      `}</style>

      {/* ── Scanline overlay ── */}
      <div style={{
        position: "fixed", inset: 0, pointerEvents: "none", zIndex: 1,
        background: "repeating-linear-gradient(0deg,transparent,transparent 2px,#00000009 2px,#00000009 4px)",
      }} />

      {/* ── Header ── */}
      <div style={{
        borderBottom: "1px solid #0f1623", padding: "22px 40px",
        display: "flex", justifyContent: "space-between", alignItems: "center",
        background: "linear-gradient(180deg,#080C14,transparent)",
        position: "sticky", top: 0, zIndex: 10, backdropFilter: "blur(14px)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <span style={{
            fontSize: 22, fontFamily: "'Space Mono',monospace", fontWeight: 700,
            background: "linear-gradient(135deg,#00FFB2,#38BDF8)", WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent", backgroundSize: "200% auto",
            animation: "shimmer 4s linear infinite",
          }}>AGENTIC_AI</span>
          <div style={{ width: 1, height: 22, background: "#1F2937" }} />
          <span style={{ fontSize: 10, color: "#374151", fontFamily: "'Courier New',monospace", letterSpacing: ".16em" }}>
            MULTI-AGENT RESEARCH ORCHESTRATOR
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 7, height: 7, borderRadius: "50%",
            background: running ? "#00FFB2" : "#1F2937",
            animation: running ? "blink 1s infinite" : "none",
            boxShadow: running ? "0 0 8px #00FFB2" : "none",
          }} />
          <span style={{ fontSize: 10, color: "#374151", fontFamily: "'Courier New',monospace", letterSpacing: ".1em" }}>
            {running ? "PIPELINE ACTIVE" : "STANDBY"}
          </span>
        </div>
      </div>

      <div style={{ padding: "36px 40px", maxWidth: 1380, margin: "0 auto" }}>

        {/* ── Query input ── */}
        <div style={{
          marginBottom: 28, background: "#080C14", border: "1px solid #1F2937",
          borderRadius: 12, padding: 26, position: "relative", overflow: "hidden",
        }}>
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 1, background: "linear-gradient(90deg,transparent,#00FFB244,transparent)" }} />
          <div style={{ fontSize: 10, color: "#374151", fontFamily: "'Courier New',monospace", letterSpacing: ".15em", marginBottom: 12 }}>
            ── MISSION INPUT ──────────────────────────────────────────────────
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <div style={{ flex: 1, position: "relative" }}>
              <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "#00FFB2", fontFamily: "'Courier New',monospace", pointerEvents: "none" }}>›</span>
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === "Enter" && runPipeline()}
                placeholder="Define your research mission…  e.g. 'Latest advancements in AI memory systems'"
                style={{
                  width: "100%", padding: "13px 14px 13px 32px",
                  background: "#020810", border: "1px solid #1F2937", borderRadius: 8,
                  color: "#F9FAFB", fontFamily: "'Courier New',monospace", fontSize: 13, outline: "none",
                  transition: "border-color .2s",
                }}
                onFocus={e => e.target.style.borderColor = "#00FFB244"}
                onBlur={e => e.target.style.borderColor = "#1F2937"}
              />
            </div>
            <button onClick={runPipeline} disabled={running || !query.trim()} style={{
              padding: "13px 26px", borderRadius: 8, cursor: running || !query.trim() ? "not-allowed" : "pointer",
              background: running || !query.trim() ? "transparent" : "linear-gradient(135deg,#00FFB215,#38BDF815)",
              border: `1px solid ${running || !query.trim() ? "#1F2937" : "#00FFB244"}`,
              color: running || !query.trim() ? "#374151" : "#00FFB2",
              fontFamily: "'Space Mono',monospace", fontSize: 11, letterSpacing: ".12em",
              transition: "all .3s", whiteSpace: "nowrap",
            }}>
              {running ? "◈ RUNNING…" : "▶ RUN PIPELINE"}
            </button>
            <button onClick={reset} style={{
              padding: "13px 18px", borderRadius: 8, cursor: "pointer",
              background: "transparent", border: "1px solid #1F2937",
              color: "#4B5563", fontFamily: "'Space Mono',monospace", fontSize: 11, transition: "all .2s",
            }}
              onMouseEnter={e => { e.target.style.borderColor = "#374151"; e.target.style.color = "#9CA3AF"; }}
              onMouseLeave={e => { e.target.style.borderColor = "#1F2937"; e.target.style.color = "#4B5563"; }}
            >↺ RESET</button>
          </div>

          {/* error banner */}
          {error && (
            <div style={{
              marginTop: 12, padding: "10px 14px", borderRadius: 6,
              background: "#150505", border: "1px solid #ef444433",
              color: "#ef4444", fontFamily: "'Courier New',monospace", fontSize: 11,
            }}>
              ✗ {error}
            </div>
          )}
        </div>

        {/* ── Pipeline progress bar ── */}
        <PipelineBar agentStates={agentStates} />

        {/* ── Agent cards grid ── */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 18, marginBottom: 0 }}>
          {AGENTS.map(agent => (
            <AgentCard
              key={agent.id}
              agent={agent}
              state={agentStates[agent.id]}
              logs={agentLogs[agent.id]}
              data={agentData[agent.id]}
            />
          ))}
        </div>

        {/* ── Result panel ── */}
        <ResultPanel result={result} />

        {/* ── Stats footer ── */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginTop: 22 }}>
          {[
            { label: "AGENTS ACTIVE",   value: activeCount,    color: "#00FFB2" },
            { label: "PHASES DONE",     value: completedCount, color: "#22c55e" },
            { label: "PIPELINE STEPS",  value: 4,              color: "#38BDF8" },
            { label: "REPORT READY",    value: result ? "YES" : "NO", color: "#A78BFA" },
          ].map(s => (
            <div key={s.label} style={{
              background: "#080C14", border: "1px solid #1F2937", borderRadius: 8, padding: "14px", textAlign: "center",
            }}>
              <div style={{ fontSize: 26, fontFamily: "'Space Mono',monospace", fontWeight: 700, color: s.color, marginBottom: 4 }}>
                {s.value}
              </div>
              <div style={{ fontSize: 9, color: "#4B5563", fontFamily: "'Courier New',monospace", letterSpacing: ".14em" }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
