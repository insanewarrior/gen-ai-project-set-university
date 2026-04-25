export default function FollowupChip({ question, onSelect }) {
  function handleKeyDown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onSelect(question)
    }
  }

  return (
    <button
      role="button"
      aria-label={`Ask follow-up: ${question}`}
      onClick={() => onSelect(question)}
      onKeyDown={handleKeyDown}
      className="text-xs px-3 py-1.5 rounded-full border border-zinc-700 text-zinc-400 bg-zinc-900 hover:border-blue-500 hover:text-blue-400 transition-colors cursor-pointer"
    >
      {question}
    </button>
  )
}
