'use client';

import { useState, useEffect, useRef } from 'react';

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  );
}

function ToolBadge({ name }) {
  const isAdmin = name !== 'chat';
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 10px',
        borderRadius: '6px',
        background: isAdmin ? 'rgba(74, 222, 128, 0.08)' : 'rgba(255,255,255,0.05)',
        border: isAdmin ? '1px solid rgba(74, 222, 128, 0.25)' : '1px solid transparent',
        fontSize: '13px',
        transition: 'all 0.3s ease',
      }}
    >
      <span
        style={{
          width: '7px',
          height: '7px',
          borderRadius: '50%',
          background: isAdmin ? '#4ade80' : '#60a5fa',
          boxShadow: isAdmin ? '0 0 6px #4ade80' : 'none',
          flexShrink: 0,
        }}
      />
      <span style={{ color: isAdmin ? '#4ade80' : 'rgba(255,255,255,0.75)' }}>{name}</span>
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', padding: '2px 0' }}>
      <div style={{ maxWidth: '72%' }}>
        {!isUser && (
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginBottom: '4px', paddingLeft: '2px' }}>
            AgentZero{msg.toolUsed ? ` · called ${msg.toolUsed}` : ''}
          </div>
        )}
        <div
          style={{
            background: isUser ? '#2f2f2f' : 'transparent',
            borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
            padding: isUser ? '10px 16px' : '2px 0',
            fontSize: '14px',
            lineHeight: '1.6',
            color: isUser ? 'white' : 'rgba(255,255,255,0.88)',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {msg.content}
        </div>
      </div>
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start', padding: '2px 0' }}>
      <div>
        <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginBottom: '4px' }}>AgentZero</div>
        <div style={{ display: 'flex', gap: '5px', padding: '8px 0' }}>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className={`dot-${i + 1}`}
              style={{ display: 'block', width: '7px', height: '7px', borderRadius: '50%', background: 'rgba(255,255,255,0.4)' }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [token, setToken] = useState('');
  const [booting, setBooting] = useState(true);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const init = async () => {
      const saved = typeof window !== 'undefined' ? localStorage.getItem('token') || '' : '';
      if (saved) {
        setToken(saved);
        setBooting(false);
        return;
      }
      try {
        const res = await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: '{}',
        });
        const data = await res.json();
        if (res.ok && data.token) {
          localStorage.setItem('token', data.token);
          setToken(data.token);
        }
      } catch {}
      setBooting(false);
    };
    init();
  }, []);

  const loadTools = async (override) => {
    const tk = override !== undefined ? override : token;
    try {
      const res = await fetch('/api/tools', {
        headers: tk ? { Authorization: `Bearer ${tk}` } : {},
      });
      const data = await res.json();
      setTools(data.tools || []);
    } catch {
      setTools([]);
    }
  };

  useEffect(() => {
    if (!token) return;
    loadTools(token);
    const id = setInterval(() => loadTools(), 2500);
    return () => clearInterval(id);
  }, [token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response || data.error || 'No response', toolUsed: data.tool_used },
      ]);
      await loadTools();
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error contacting the agent. Please try again.' },
      ]);
    }
    setLoading(false);
    inputRef.current?.focus();
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (booting) {
    return (
      <div style={{ height: '100vh', background: '#212121', color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Initializing session...
      </div>
    );
  }

  if (!token) {
    return (
      <div style={{ height: '100vh', background: '#212121', color: '#f87171', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Unable to initialize session
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#212121', color: 'white' }}>
      <div
        style={{
          width: '260px',
          flexShrink: 0,
          background: '#171717',
          borderRight: '1px solid rgba(255,255,255,0.08)',
          display: 'flex',
          flexDirection: 'column',
          padding: '20px 16px',
          gap: '24px',
          overflowY: 'auto',
        }}
      >
        <div>
          <div style={{ fontSize: '17px', fontWeight: 600, letterSpacing: '-0.3px' }}>AgentZero</div>
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginTop: '2px' }}>v0.1.0 · AI Assistant</div>
        </div>

        <div>
          <div
            style={{
              fontSize: '10px',
              fontWeight: 600,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.4)',
              marginBottom: '8px',
            }}
          >
            Available Tools
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {tools.length === 0 && (
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.25)', padding: '4px 2px' }}>Loading…</div>
            )}
            {tools.map((t) => (
              <ToolBadge key={t} name={t} />
            ))}
          </div>
        </div>

        <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.18)', lineHeight: '1.6' }}>
            Customize your session
          </div>
          <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.28)', fontFamily: 'monospace' }}>
            POST /api/preferences
          </div>
        </div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {messages.length === 0 && !loading && (
            <div
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'rgba(255,255,255,0.2)',
                fontSize: '14px',
                userSelect: 'none',
              }}
            >
              Send a message to start chatting
            </div>
          )}
          {messages.map((msg, i) => (
            <Message key={i} msg={msg} />
          ))}
          {loading && <ThinkingIndicator />}
          <div ref={bottomRef} />
        </div>

        <div style={{ padding: '0 32px 28px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              background: '#2f2f2f',
              borderRadius: '16px',
              padding: '12px 16px',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Message AgentZero…"
              rows={1}
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'white',
                fontSize: '14px',
                resize: 'none',
                lineHeight: '1.5',
                maxHeight: '120px',
                overflowY: 'auto',
                fontFamily: 'inherit',
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{
                background: input.trim() && !loading ? 'white' : 'rgba(255,255,255,0.15)',
                border: 'none',
                borderRadius: '8px',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                color: input.trim() && !loading ? '#212121' : 'rgba(255,255,255,0.3)',
                flexShrink: 0,
                transition: 'all 0.15s',
              }}
            >
              <SendIcon />
            </button>
          </div>
          <div style={{ textAlign: 'center', marginTop: '8px', fontSize: '11px', color: 'rgba(255,255,255,0.2)' }}>
            AgentZero may make mistakes. Check important info.
          </div>
        </div>
      </div>
    </div>
  );
}
