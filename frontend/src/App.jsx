import React, { useState, useRef, useEffect } from 'react'
import './chat.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

function App() {
  const [isOpen, setIsOpen] = useState(true)
  const [voiceMode, setVoiceMode] = useState(false)
  const [language, setLanguage] = useState(null) // null means no language selected yet
  const [showLanguageSelector, setShowLanguageSelector] = useState(true)
  const [typing, setTyping] = useState(false)
  const [messages, setMessages] = useState([])

  // Language options with native scripts
  const languageOptions = [
    { code: 'en', name: 'English', native: 'English' },
    { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
    { code: 'kha', name: 'Khasi', native: 'Khasi' },
    { code: 'mwr', name: 'Marwari', native: 'मारवाड़ी' },
    { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
    { code: 'te', name: 'Telugu', native: 'తెలుగు' },
    { code: 'bn', name: 'Bengali', native: 'বাংলা' },
    { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
  ]

  // Welcome messages for different languages
  const welcomeMessages = {
    'en': 'Hi! Ask me anything about college admissions, fees, hostel facilities, or exam schedules. How can I help you today?',
    'hi': 'नमस्ते! College admission, fees, hostel facilities, या exam schedules के बारे में कुछ भी पूछिए। आज मैं आपकी कैसे मदद कर सकता हूं?',
    'kha': 'Khublei! College admission, fees, hostel facilities, bad exam schedules jingrwai ka jingim ne juki. Kumno nga buh jingkynmaw ia phi da ka sngi?',
    'mwr': 'नमस्कार! College admission, fees, hostel facilities, या exam schedules के बारे में कुछ भी पूछो। आज मैं थारी कैसे मदद करूं?',
    'ta': 'வணக்கம்! College admission, fees, hostel facilities, அல்லது exam schedules பற்றி எதுவும் கேளுங்கள். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?',
    'te': 'నమస్కారం! College admission, fees, hostel facilities, లేదా exam schedules గురించి ఏదైనా అడగండి. ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?',
    'bn': 'নমস্কার! College admission, fees, hostel facilities, বা exam schedules সম্পর্কে যেকোনো কিছু জিজ্ঞাসা করুন। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?',
    'gu': 'નમસ્તે! College admission, fees, hostel facilities, કે exam schedules વિશે કંઈપણ પૂછો। આજે હું તમારી કેવી રીતે મદદ કરી શકું?'
  }
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const containerRef = useRef(null)
  // size & resize state
  const [size, setSize] = useState({ w: 360, h: 520 })
  const dragRef = useRef({ resizing: false, startX: 0, startY: 0, startW: 0, startH: 0 })

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages, typing])

  const send = async () => {
    const text = input.trim()
    if (!text || typing) return
    
    // push user message
    const userMsg = { role: 'user', text, id: Date.now() }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setTyping(true)
    
    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question: text, 
          language: language,
          ...(sessionId && { session_id: sessionId })
        }),
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      setMessages((m) => [...m, { 
        role: 'bot', 
        text: data.answer, 
        id: Date.now() + 1,
        conversationId: data.conversation_id,
        confidence: data.confidence 
      }])
      
      // Update session ID if new
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id)
      }
      
    } catch (error) {
      console.error('Error:', error)
      
      // Try to get more detailed error information
      let errorMessage = 'Sorry, I encountered an error. Please try again.'
      
      if (error.message) {
        errorMessage = `Error: ${error.message}`
      }
      
      // If it's a fetch error, try to get response details
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessage = `Network Error: Cannot connect to server. Make sure backend is running on http://127.0.0.1:8000`
      }
      
      setMessages((m) => [...m, { 
        role: 'bot', 
        text: errorMessage, 
        id: Date.now() + 1,
        isError: true 
      }])
    } finally {
      setTyping(false)
    }
  }

  const handleFeedback = async (messageIndex, feedback) => {
    const message = messages[messageIndex]
    if (!message.conversationId) return
    
    try {
      const response = await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          conversation_id: message.conversationId, 
          feedback 
        }),
      })
      
      if (response.ok) {
        setMessages(prev => prev.map((msg, i) => 
          i === messageIndex ? { ...msg, feedback } : msg
        ))
      }
      
    } catch (error) {
      console.error('Error submitting feedback:', error)
    }
  }

  const handleForwardToAdmin = async (messageIndex) => {
    const message = messages[messageIndex]
    if (!message.conversationId) return
    
    try {
      const response = await fetch(`${API_BASE}/forward-to-admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          conversation_id: message.conversationId,
          additional_context: "User requested admin assistance" 
        }),
      })
      
      if (response.ok) {
        setMessages(prev => [...prev, { 
          role: 'bot', 
          text: 'Your question has been forwarded to our support team. They will respond soon.',
          id: Date.now(),
          isSystemMessage: true
        }])
      }
      
    } catch (error) {
      console.error('Error forwarding to admin:', error)
      setMessages(prev => [...prev, { 
        role: 'bot', 
        text: 'Sorry, could not forward your message. Please try again.',
        id: Date.now(),
        isError: true
      }])
    }
  }

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  // Resize handlers
  const onResizeStart = (e) => {
    e.preventDefault()
    const isMouse = e.type === 'mousedown'
    const clientX = isMouse ? e.clientX : e.touches[0].clientX
    const clientY = isMouse ? e.clientY : e.touches[0].clientY
    dragRef.current = {
      resizing: true,
      startX: clientX,
      startY: clientY,
      startW: size.w,
      startH: size.h,
    }
    window.addEventListener('mousemove', onResizing)
    window.addEventListener('mouseup', onResizeEnd)
    window.addEventListener('touchmove', onResizing, { passive: false })
    window.addEventListener('touchend', onResizeEnd)
  }
  const onResizing = (e) => {
    if (!dragRef.current.resizing) return
    const isMouse = e.type === 'mousemove'
    const clientX = isMouse ? e.clientX : (e.touches?.[0]?.clientX || 0)
    const clientY = isMouse ? e.clientY : (e.touches?.[0]?.clientY || 0)
    const dx = clientX - dragRef.current.startX
    const dy = clientY - dragRef.current.startY
    const minW = 300, minH = 380, maxW = 640, maxH = Math.round(window.innerHeight * 0.88)
    const newW = Math.max(minW, Math.min(maxW, dragRef.current.startW + dx))
    const newH = Math.max(minH, Math.min(maxH, dragRef.current.startH + dy))
    setSize({ w: newW, h: newH })
    e.preventDefault?.()
  }
  const onResizeEnd = () => {
    dragRef.current.resizing = false
    window.removeEventListener('mousemove', onResizing)
    window.removeEventListener('mouseup', onResizeEnd)
    window.removeEventListener('touchmove', onResizing)
    window.removeEventListener('touchend', onResizeEnd)
  }

  const selectLanguage = (langCode) => {
    setLanguage(langCode)
    setShowLanguageSelector(false)
    setMessages([{ 
      role: 'bot', 
      text: welcomeMessages[langCode] || welcomeMessages['en'],
      id: Date.now()
    }])
  }

  return (
    <div>
      {!isOpen && (
        <button className="chat-launcher" onClick={() => setIsOpen(true)} aria-label="Open chat">
          ✨
        </button>
      )}
      
      {/* Language Selection Overlay */}
      {showLanguageSelector && isOpen && (
        <div className="language-overlay">
          <div className="language-modal">
            <h3>Choose Your Language</h3>
            <p>भाषा चुनें | Choose Language | আপনার ভাষা নির্বাচন করুন</p>
            <div className="language-grid">
              {languageOptions.map(lang => (
                <button 
                  key={lang.code}
                  className="language-option"
                  onClick={() => selectLanguage(lang.code)}
                >
                  <div className="native-text">{lang.native}</div>
                  <div className="english-text">{lang.name}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div
        className={`chat-wrap floating ${isOpen ? 'open' : 'closed'} ${showLanguageSelector ? 'blurred' : ''}`}
        style={{ width: size.w, height: size.h }}
      >
        <div className="chat-header">
          <div className="title">SIH Bot</div>
          <div className={`status ${typing ? 'typing' : ''}`}>{typing ? <Dots /> : 'online'}</div>
          <button className="close" onClick={() => setIsOpen(false)} aria-label="Close chat">×</button>
        </div>

        <div className="chat-body" ref={containerRef}>
          {messages.map((m, i) => (
            <div key={i} className={`message-wrapper ${m.role}`}>
              <div className={`msg ${m.role} ${m.role === 'user' ? 'in-right' : 'in-left'}`}>
                {m.text}
              </div>
              {m.role === 'bot' && !typing && i === messages.length - 1 && (
                <div className="message-actions">
                  <button 
                    className="feedback-btn thumbs-up" 
                    onClick={() => handleFeedback(i, 1)}
                    title="Helpful"
                  >
                    👍
                  </button>
                  <button 
                    className="feedback-btn thumbs-down" 
                    onClick={() => handleFeedback(i, -1)}
                    title="Not helpful"
                  >
                    👎
                  </button>
                  <button 
                    className="forward-btn" 
                    onClick={() => handleForwardToAdmin(i)}
                    title="Forward to admin"
                  >
                    ↗️
                  </button>
                </div>
              )}
            </div>
          ))}
          {typing && (
            <div className="message-wrapper bot">
              <div className="msg bot typing-bubble in-left">
                <Dots />
              </div>
            </div>
          )}
        </div>

        <div className="chat-controls">
          <div className="options">
            <label className="toggle">
              <input type="checkbox" checked={voiceMode} onChange={(e) => setVoiceMode(e.target.checked)} />
              <span className="slider"></span>
              <span className="label">Voice mode</span>
            </label>
            <div className="lang-select">
              <select 
                value={language || ''}
                onChange={(e) => {
                  const newLang = e.target.value
                  selectLanguage(newLang)
                }}
              >
                <option value="" disabled>Select Language</option>
                {languageOptions.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.native} ({lang.name})
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="chat-input">
            <button 
              className={`voice-btn ${voiceMode ? 'recording' : ''}`}
              onClick={() => setVoiceMode(!voiceMode)}
              disabled={typing}
              title={voiceMode ? "Stop recording" : "Voice input"}
            >
              🎤
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder={voiceMode ? "Listening..." : "Type your message..."}
              rows={2}
              disabled={voiceMode}
            />
            <button className="send" onClick={send} disabled={typing || (!input.trim() && !voiceMode)}>
              {voiceMode ? "🎙️" : "Send"}
            </button>
          </div>
        </div>
        <div
          className="resizer"
          onMouseDown={onResizeStart}
          onTouchStart={onResizeStart}
          role="separator"
          aria-orientation="both"
          aria-label="Resize chat"
        />
      </div>
    </div>
  )
}

function Dots() {
  return (
    <span className="dots" aria-label="typing">
      <span></span><span></span><span></span>
    </span>
  )
}

export default App
