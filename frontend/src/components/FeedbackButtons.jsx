import { useState } from 'react'
import { postFeedback } from '../api'

export default function FeedbackButtons({ queryId }) {
  const [selected, setSelected] = useState(null) // 'up' | 'down' | null

  async function handleFeedback(rating) {
    if (selected !== null || !queryId) return
    setSelected(rating)
    try {
      await postFeedback(queryId, rating)
    } catch {
      // silent fail — local selection already shown
    }
  }

  return (
    <div className="flex gap-2 mt-1" aria-label="Rate this response">
      <button
        onClick={() => handleFeedback('up')}
        disabled={selected !== null}
        aria-label="Thumbs up"
        aria-pressed={selected === 'up'}
        className={`text-base transition-colors disabled:cursor-default ${
          selected === 'up'
            ? 'text-blue-400'
            : selected !== null
              ? 'text-zinc-600'
              : 'text-zinc-500 hover:text-zinc-300'
        }`}
      >
        👍
      </button>
      <button
        onClick={() => handleFeedback('down')}
        disabled={selected !== null}
        aria-label="Thumbs down"
        aria-pressed={selected === 'down'}
        className={`text-base transition-colors disabled:cursor-default ${
          selected === 'down'
            ? 'text-amber-400'
            : selected !== null
              ? 'text-zinc-600'
              : 'text-zinc-500 hover:text-zinc-300'
        }`}
      >
        👎
      </button>
    </div>
  )
}
