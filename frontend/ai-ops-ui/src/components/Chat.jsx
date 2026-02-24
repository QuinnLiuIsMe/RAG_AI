import React, { useEffect, useRef, useState } from "react";
import "./Chat.css";

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const feedRef = useRef(null);

  useEffect(() => {
    if (!feedRef.current) return;
    feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [messages, isLoading]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    const newMessages = [...messages, { role: "user", content: question }];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
        }),
      });
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      const data = await response.json();
      const answer =
        typeof data.answer === "string" && data.answer.trim()
          ? data.answer
          : "I received a response, but it did not include an answer.";

      setMessages([
        ...newMessages,
        { role: "agent", content: answer },
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { role: "agent", content: "Error: " + err.message },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="aiops-page">
      <div className="bg-orb orb-a" aria-hidden="true" />
      <div className="bg-orb orb-b" aria-hidden="true" />
      <div className="grid-overlay" aria-hidden="true" />

      <section className="chat-shell">
        <header className="chat-header">
          <p className="eyebrow">AI Steering</p>
          <h1>Ops Copilot Console</h1>
          <p className="subtitle">
            Ask operational questions and get realtime answers from your agent.
          </p>
        </header>

        <div className="message-panel" ref={feedRef}>
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Ready when you are.</p>
              <span>Try: "Summarize failed deployments in the last 24 hours."</span>
            </div>
          )}

          {messages.map((m, idx) => (
            <article
              key={idx}
              className={`message-row ${m.role === "user" ? "user" : "agent"}`}
            >
              <p className="message-author">{m.role === "user" ? "You" : "Agent"}</p>
              <p className="message-content">{m.content}</p>
            </article>
          ))}

          {isLoading && (
            <article className="message-row agent loading" aria-live="polite">
              <p className="message-author">Agent</p>
              <p className="message-content typing">
                <span />
                <span />
                <span />
              </p>
            </article>
          )}
        </div>

        <div className="composer">
          <textarea
            rows={2}
            placeholder="What do you want to investigate?"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button onClick={handleSend} disabled={isLoading || !input.trim()}>
            {isLoading ? "Thinking..." : "Send"}
          </button>
        </div>
      </section>
    </main>
  );
}
