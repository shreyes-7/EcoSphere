import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, Send, Bot, User, Sparkles, Cpu, Loader2, CheckCircle } from 'lucide-react';

export default function FacilityManagerChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputMsg, setInputMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      text: 'Hello! I am your AI Facility Manager. Ask me anything about building performance, digital twin, occupancy energy waste, or supervisor decisions.',
      tool_calls: [],
      suggested_followups: ['Show digital twin status', 'Are there any energy waste warnings?', 'Why did supervisor change setpoint?']
    }
  ]);

  const chatEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend) => {
    const query = textToSend || inputMsg;
    if (!query.trim() || loading) return;

    const userMsg = { id: Date.now(), role: 'user', text: query };
    setMessages((prev) => [...prev, userMsg]);
    setInputMsg('');
    setLoading(true);

    try {
      const res = await fetch('/facility-manager/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query, conversation_id: 'session_ui' })
      });

      if (res.ok) {
        const data = await res.json();
        const aiMsg = {
          id: Date.now() + 1,
          role: 'assistant',
          text: data.reply,
          tool_calls: data.tool_calls || [],
          suggested_followups: data.suggested_followups || []
        };
        setMessages((prev) => [...prev, aiMsg]);
      } else {
        setMessages((prev) => [
          ...prev,
          { id: Date.now() + 1, role: 'assistant', text: 'Sorry, I encountered an issue connecting to the facility manager backend.' }
        ]);
      }
    } catch (err) {
      console.error("Facility manager chat error:", err);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', text: 'Unable to reach facility manager service.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Chatbot Launcher Button */}
      <motion.button
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.92 }}
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 p-4 rounded-2xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 text-slate-950 shadow-2xl shadow-emerald-500/30 flex items-center gap-2.5 font-bold text-xs select-none"
      >
        <Bot className="w-5 h-5" />
        <span className="hidden sm:inline">AI Facility Manager</span>
        <Sparkles className="w-3.5 h-3.5" />
      </motion.button>

      {/* Floating Chat Modal Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-full max-w-lg h-[540px] amoled-card rounded-3xl border border-emerald-500/40 shadow-2xl flex flex-col justify-between overflow-hidden"
          >
            {/* Window Header */}
            <div className="p-4 bg-[#03060c] border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-slate-950 font-black">
                  <Bot className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-extrabold text-white leading-tight">AI Facility Manager</h4>
                  <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Tool-Calling Intelligence Online
                  </span>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Chat Conversation History */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs font-sans">
              {messages.map((m) => (
                <div key={m.id} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`max-w-[85%] p-3.5 rounded-2xl leading-relaxed ${
                      m.role === 'user'
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold rounded-br-none'
                        : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-bl-none shadow-lg'
                    }`}
                  >
                    {m.text}
                  </div>

                  {/* Executed Tools Badge List */}
                  {m.tool_calls && m.tool_calls.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {m.tool_calls.map((t, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 text-[10px] font-mono flex items-center gap-1">
                          <CheckCircle className="w-3 h-3 text-emerald-400" /> Executed Tool: {t.tool_name}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Suggested Followups */}
                  {m.suggested_followups && m.suggested_followups.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {m.suggested_followups.map((s, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(s)}
                          className="px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-slate-300 hover:border-emerald-500/50 hover:text-emerald-300 text-[10px] transition"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="flex items-center gap-2 text-slate-400 text-xs font-mono">
                  <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>AI Facility Manager is executing backend tools...</span>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="p-3 bg-[#03060c] border-t border-slate-800 flex items-center gap-2"
            >
              <input
                type="text"
                value={inputMsg}
                onChange={(e) => setInputMsg(e.target.value)}
                placeholder="Ask about digital twin, energy waste, supervisor..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
              <button
                type="submit"
                disabled={loading || !inputMsg.trim()}
                className="p-2 rounded-xl bg-emerald-500 text-slate-950 disabled:opacity-50 hover:bg-emerald-400 transition"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
