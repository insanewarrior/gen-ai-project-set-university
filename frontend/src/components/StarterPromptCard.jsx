export default function StarterPromptCard({ question, onSelect }) {
  function handleKeyDown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onSelect(question)
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onSelect(question)}
      onKeyDown={handleKeyDown}
      className="bg-surface rounded-xl p-4 cursor-pointer transition-colors border border-border hover:border-[#b8ff3c33] hover:bg-surface-2 text-sm text-text-secondary hover:text-white"
    >
      {question}
    </div>
  )
}
