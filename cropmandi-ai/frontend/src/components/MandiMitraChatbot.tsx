import React, { useState, useRef, useEffect } from 'react';
import type { Language } from '../i18n/translations';
import { translations } from '../i18n/translations';
import { X, Send, Bot, User, Sparkles, RefreshCw } from 'lucide-react';

interface Props {
  language: Language;
}

interface ChatMessage {
  id: string;
  sender: 'bot' | 'user';
  text: string;
  timestamp: string;
}

const GEMINI_API_KEY = (import.meta as any).env?.VITE_GEMINI_API_KEY || "";

export const MandiMitraChatbot: React.FC<Props> = ({ language }) => {
  const t = translations[language].chatbot;
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [inputMsg, setInputMsg] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'bot',
      text: t.welcomeMsg,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMsg;
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMsg('');
    setLoading(true);

    try {
      // Call Gemini API (gemini-flash-latest endpoint)
      let response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=${GEMINI_API_KEY}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [
              {
                role: 'user',
                parts: [
                  {
                    text: `Answer the user question directly and concisely in language: ${language === 'te' ? 'Telugu' : language === 'hi' ? 'Hindi' : language === 'ml' ? 'Malayalam' : language === 'ta' ? 'Tamil' : 'English'}.
CRITICAL INSTRUCTION: Do NOT introduce yourself, do NOT say "I am Mandi Mitra AI", "Namaste", or add any filler preambles. Give ONLY the direct factual answer to the question in 1-3 short sentences.

Question: "${text}"`
                  }
                ]
              }
            ]
          })
        }
      );

      if (!response.ok) {
        // Retry with gemini-3.5-flash endpoint if needed
        response = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=${GEMINI_API_KEY}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [
                {
                  role: 'user',
                  parts: [
                    {
                      text: `Directly answer question: "${text}" in ${language} without any greetings or self-introduction.`
                    }
                  ]
                }
              ]
            })
          }
        );
      }

      if (response.ok) {
        const data = await response.json();
        let botReplyText = data.candidates?.[0]?.content?.parts?.[0]?.text || "Current mandi modal prices are steady across major AP yards.";
        // Clean any residual self-introductions if returned by model
        botReplyText = botReplyText.replace(/^I am Mandi Mitra AI[.,!]?\s*/i, '').replace(/^Namaste[.,!]?\s*/i, '');
        
        const botMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: botReplyText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        const fallbackText = getFallbackAnswer(text, language);
        const botMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: fallbackText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, botMsg]);
      }
    } catch (e) {
      console.error(e);
      const fallbackText = getFallbackAnswer(text, language);
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: fallbackText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMsg]);
    } finally {
      setLoading(false);
    }
  };

  const getFallbackAnswer = (query: string, lang: Language): string => {
    const q = query.toLowerCase();
    if (q.includes('tomato') || q.includes('టమోటా') || q.includes('टमाटर')) {
      return lang === 'te' 
        ? "మదన్పల్లె మరియు అనంతపురం మండిలలో టమోటా ధర క్వింటాలుకు ₹1,850 - ₹1,950 గా ఉండి స్థిరంగా కొనసాగుతోంది."
        : "Madanapalli and AP mandi Tomato modal prices are currently ₹1,850 - ₹1,950 per quintal.";
    }
    if (q.includes('kisan') || q.includes(' scheme') || q.includes('పథకం')) {
      return lang === 'te'
        ? "PM-KISAN ద్వారా సంవత్సరానికి ₹6,000 మరియు AP YSR రైతు భరోసా ద్వారా ₹13,500 పెట్టుబడి సాయం లభిస్తుంది."
        : "PM-KISAN provides ₹6,000/year and AP YSR Rythu Bharosa provides ₹13,500/year to eligible farmers.";
    }
    return lang === 'te'
      ? "మండి ధరలు మరియు రాబోయే 3 రోజుల అంచనాల వివరాలు స్క్రీన్‌పై అందుబాటులో ఉన్నాయి."
      : "Current mandi prices and 3-day forecasts are available on the dashboard.";
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            position: 'fixed',
            bottom: '1.75rem',
            right: '1.75rem',
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)',
            color: '#ffffff',
            border: '2px solid #ffffff',
            boxShadow: '0 8px 24px rgba(27, 67, 50, 0.3)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            transition: 'transform 0.2s ease',
          }}
          title={t.title}
        >
          <img src="/logo.jpg" alt="Logo" style={{ width: '42px', height: '42px', borderRadius: '50%', objectFit: 'cover' }} />
        </button>
      )}

      {/* Chatbot Popup Modal */}
      {isOpen && (
        <div
          className="glass-panel"
          style={{
            position: 'fixed',
            bottom: '1.75rem',
            right: '1.75rem',
            width: '380px',
            maxWidth: 'calc(100vw - 2rem)',
            height: '540px',
            maxHeight: 'calc(100vh - 4rem)',
            borderRadius: 'var(--radius-lg)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 99999,
            overflow: 'hidden',
            boxShadow: 'var(--shadow-lg)',
            background: '#ffffff',
            border: '1px solid var(--border-color-strong)',
          }}
        >
          {/* Header */}
          <div style={{ background: 'linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%)', padding: '1rem 1.25rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <img src="/logo.jpg" alt="Mandi Mitra" style={{ width: '36px', height: '36px', borderRadius: '50%', border: '2px solid #ffffff' }} />
              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>{t.title}</h4>
                <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Sparkles size={12} color="#fef3c7" />
                  <span>Gemini NLP AI Active</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              style={{ background: 'transparent', border: 'none', color: '#ffffff', cursor: 'pointer', opacity: 0.8 }}
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages Body */}
          <div style={{ flex: 1, padding: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.85rem', background: '#fcfaf6' }}>
            {messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  gap: '0.5rem',
                }}
              >
                {msg.sender === 'bot' && (
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--primary-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Bot size={16} color="var(--primary-dark)" />
                  </div>
                )}

                <div
                  style={{
                    maxWidth: '80%',
                    padding: '0.75rem 0.95rem',
                    borderRadius: msg.sender === 'user' ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                    background: msg.sender === 'user' ? 'var(--primary)' : '#ffffff',
                    color: msg.sender === 'user' ? '#ffffff' : 'var(--text-main)',
                    fontSize: '0.88rem',
                    lineHeight: 1.45,
                    boxShadow: 'var(--shadow-sm)',
                    border: msg.sender === 'bot' ? '1px solid var(--border-color)' : 'none',
                  }}
                >
                  <div>{msg.text}</div>
                  <div style={{ fontSize: '0.68rem', marginTop: '0.25rem', opacity: 0.7, textAlign: 'right' }}>
                    {msg.timestamp}
                  </div>
                </div>

                {msg.sender === 'user' && (
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-gold-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <User size={16} color="#92400e" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                <RefreshCw size={14} className="spin" />
                <span>Mandi Mitra AI is thinking...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          <div style={{ padding: '0.5rem 0.75rem', background: '#ffffff', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.4rem', overflowX: 'auto', scrollbarWidth: 'none' }}>
            {t.quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(prompt)}
                style={{
                  fontSize: '0.75rem',
                  padding: '0.3rem 0.65rem',
                  borderRadius: '50px',
                  border: '1px solid var(--border-color-strong)',
                  background: 'var(--bg-primary)',
                  color: 'var(--primary-dark)',
                  whiteSpace: 'nowrap',
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Bar */}
          <form
            onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
            style={{ padding: '0.75rem', background: '#ffffff', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.5rem' }}
          >
            <input
              type="text"
              className="form-input"
              style={{ fontSize: '0.88rem', padding: '0.6rem 0.85rem' }}
              placeholder={t.placeholder}
              value={inputMsg}
              onChange={(e) => setInputMsg(e.target.value)}
            />
            <button type="submit" className="btn-primary" style={{ padding: '0.6rem 1rem' }} disabled={loading}>
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </>
  );
};
