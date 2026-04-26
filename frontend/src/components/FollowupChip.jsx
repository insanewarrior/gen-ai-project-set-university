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
      className="text-xs px-3 py-1.5 rounded-full border border-border text-text-muted bg-bg hover:border-[#b8ff3c33] hover:text-accent transition-colors cursor-pointer"
    >
      {question}
    </button>
  )
}
