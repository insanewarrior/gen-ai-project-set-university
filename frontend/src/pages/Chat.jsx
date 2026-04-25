import { useState, useEffect, useRef } from 'react'
import { postQuery, postAnalyze, getSessions } from '../api'
import ChatBubble from '../components/ChatBubble'
import QueryCounter from '../components/QueryCounter'
import StarterPromptCard from '../components/StarterPromptCard'

const STARTER_PROMPTS = [
  "Why might my strength be inconsistent between sessions?",
  "How should I structure my weekly training?",
  "What should I focus on to improve faster?",
]

const FOLLOWUP_CHIPS = {
  low: [
    "How can I improve my training consistency?",
    "What metrics matter most for beginners?",
    "How often should I train per week?",
  ],
  medium: [
    "What patterns do you see in my recent sessions?",
    "How does my volume compare to recommendations?",
    "What should I focus on next?",
  ],
  high: [
    "What trends have developed over my training history?",
    "Where am I plateauing and why?",
    "How does my current program compare to optimal?",
  ],
}

function getFollowups(confidence) {
  return FOLLOWUP_CHIPS[confidence] ?? FOLLOWUP_CHIPS.medium
}

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [queriesRemaining, setQueriesRemaining] = useState(null)
  const [tierLimit, setTierLimit] = useState(null)
  const [resetAt, setResetAt] = useState(null)
  const [sessionCount, setSessionCount] = useState(null)
  const [error, setError] = useState(null)

  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    getSessions()
      .then(res => setSessionCount(res.data?.length ?? 99))
      .catch(() => setSessionCount(99))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  function handleInputChange(e) {
    setInput(e.target.value)
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 200) + 'px'
    }
  }

  async function submitQuery(queryText) {
    const text = queryText.trim()
    if (!text || isLoading || queriesRemaining === 0) return

    setMessages(prev => [...prev, { role: 'user', content: text }])
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    setIsLoading(true)
    setError(null)

    try {
      const isProgram = text.includes('\n')
      const data = isProgram ? await postAnalyze(text) : await postQuery(text)
      const payload = data.data
      setMessages(prev => [
        ...prev,
        {
          role: 'ai',
          content: payload.response,
          citations: payload.citations,
          confidence: payload.confidence,
        },
      ])
      setQueriesRemaining(payload.queriesRemaining ?? null)
      if (payload.tierLimit != null) setTierLimit(payload.tierLimit)
    } catch (err) {
      if (err.code === 'RATE_LIMIT_EXCEEDED') {
        setQueriesRemaining(0)
        const resetAtValue = err.detail?.detail?.resetAt ?? null
        setResetAt(resetAtValue)
        setError('Daily limit reached. Resets at ' + (resetAtValue ? formatResetTime(resetAtValue) : 'midnight') + '.')
      } else {
        setError("I couldn't process that question right now. Please try again.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  function formatResetTime(iso) {
    if (!iso) return ''
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submitQuery(input)
    }
  }

  function handleStarterSelect(question) {
    submitQuery(question)
  }

  function handleFollowupSelect(question) {
    submitQuery(question)
  }

  const showStarters = sessionCount !== null && sessionCount < 5 && messages.length === 0
  const inputDisabled = isLoading || queriesRemaining === 0

  return (
    <div className="flex flex-col h-full -m-4">
      {/* Scrollable message area */}
      <div
        role="log"
        aria-live="polite"
        aria-label="Coaching conversation"
        className="flex-1 overflow-y-auto p-4 flex flex-col gap-4"
      >
        {showStarters && (
          <div className="flex flex-col gap-3">
            <p className="text-sm text-zinc-400 text-center">The more sessions you log, the better my answers get.</p>
            {STARTER_PROMPTS.map((q, i) => (
              <StarterPromptCard key={i} question={q} onSelect={handleStarterSelect} />
            ))}
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatBubble
            key={i}
            role={msg.role}
            message={msg.content}
            citations={msg.citations}
            followups={msg.role === 'ai' ? getFollowups(msg.confidence) : undefined}
            onFollowupSelect={handleFollowupSelect}
          />
        ))}

        {isLoading && (
          <div className="flex gap-1 items-center px-4 py-3 bg-zinc-800 rounded-2xl rounded-tl-sm w-fit">
            <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
            <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
            <span className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce"></span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Inline error */}
      {error && (
        <div className="px-4 pb-2 text-sm text-red-400">{error}</div>
      )}

      {/* Query counter + input bar */}
      <div className="border-t border-zinc-700 bg-zinc-900">
        {queriesRemaining !== null && (
          <div className="px-4 pt-2 flex justify-end">
            <QueryCounter queriesRemaining={queriesRemaining} resetAt={resetAt} tierLimit={tierLimit ?? 3} />
          </div>
        )}
        <div className="p-3 flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            value={queriesRemaining === 0 ? '' : input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={inputDisabled}
            placeholder={queriesRemaining === 0
              ? `Daily limit reached. Resets at ${formatResetTime(resetAt)}.`
              : 'Ask about your training...'}
            aria-label="Ask a coaching question"
            rows={1}
            className="flex-1 resize-none bg-zinc-800 text-zinc-100 placeholder-zinc-500 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
            style={{ maxHeight: '200px' }}
          />
          <button
            onClick={() => submitQuery(input)}
            disabled={inputDisabled || !input.trim()}
            aria-label="Send question"
            className="w-10 h-10 flex-shrink-0 flex items-center justify-center bg-blue-500 hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed rounded-full transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-white">
              <path d="M3.105 2.288a.75.75 0 0 0-.826.95l1.401 4.425H11.5a.75.75 0 0 1 0 1.5H3.68l-1.401 4.425a.75.75 0 0 0 .826.95 28.896 28.896 0 0 0 15.293-7.154.75.75 0 0 0 0-1.164A28.897 28.897 0 0 0 3.105 2.288Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
