import React, { useCallback, useEffect, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem("analytics-agent-session") || "");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(scrollToBottom, [messages]);

  // Ensure we have a session on load
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem("analytics-agent-session", sessionId);
      return;
    }
    fetch(`${API_BASE}/session`, { method: "POST" })
      .then((r) => r.json())
      .then((data) => {
        const id = data.session_id;
        setSessionId(id);
        localStorage.setItem("analytics-agent-session", id);
      })
      .catch(() => {
        setMessages((m) => [...m, { role: "system", content: "Could not reach API. Is the backend running on " + API_BASE + "?" }]);
      });
  }, []);

  const onFileSelect = useCallback(async (file) => {
    if (!file || !sessionId) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${API_BASE}/upload?session_id=${encodeURIComponent(sessionId)}`, {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setUploadedFile(file.name);
      setMessages((m) => [...m, { role: "system", content: `Uploaded "${file.name}". You can ask questions about your data.` }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "system", content: "Upload failed: " + e.message }]);
    } finally {
      setUploading(false);
    }
  }, [sessionId]);

  const onDrop = useCallback(
    (e) => {
      e.preventDefault();
      const f = e.dataTransfer?.files?.[0];
      if (f) onFileSelect(f);
    },
    [onFileSelect]
  );
  const onDragOver = (e) => e.preventDefault();

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setSending(true);
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: "Error: " + e.message }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Analytics Agent</h1>
        <p>Upload Excel or CSV (export from Power BI), then ask questions like a data analyst.</p>
      </header>

      <div
        className={`upload-zone ${uploadedFile ? "has-file" : ""}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
      >
        <input
          type="file"
          id="file"
          accept=".xlsx,.xls,.csv"
          onChange={(e) => onFileSelect(e.target.files?.[0])}
          disabled={uploading}
        />
        <label htmlFor="file">
          {uploading ? "Uploading…" : uploadedFile ? `Uploaded: ${uploadedFile}` : "Choose file or drop here"}
        </label>
        <p className="hint">Supported: .xlsx, .xls, .csv (Power BI: export to Excel or CSV first)</p>
      </div>

      <section className="chat-section">
        <div className="messages">
          {messages.length === 0 && (
            <div className="message system">
              Upload a file above, then ask things like: &quot;What are the top 5 rows?&quot;, &quot;Summarize the Sales column&quot;, &quot;How many rows?&quot;
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <form
          className="chat-form"
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
        >
          <input
            type="text"
            placeholder="Ask about your data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={sending}
          />
          <button type="submit" disabled={sending}>
            Send
          </button>
        </form>
      </section>
    </div>
  );
}

export default App;
