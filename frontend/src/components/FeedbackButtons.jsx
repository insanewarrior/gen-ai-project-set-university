import { useState } from 'react'
import { ThumbsUp, ThumbsDown } from 'lucide-react'
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
        className="transition-colors disabled:cursor-default"
      >
        <ThumbsUp
          size={15}
          strokeWidth={2}
          color={selected === 'up' ? '#00aaff' : selected !== null ? '#3f3f46' : '#71717a'}
        />
      </button>
      <button
        onClick={() => handleFeedback('down')}
        disabled={selected !== null}
        aria-label="Thumbs down"
        aria-pressed={selected === 'down'}
        className="transition-colors disabled:cursor-default"
      >
        <ThumbsDown
          size={15}
          strokeWidth={2}
          color={selected === 'down' ? '#bf00ff' : selected !== null ? '#3f3f46' : '#71717a'}
        />
      </button>
    </div>
  )
}
