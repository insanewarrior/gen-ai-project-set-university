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
      className="bg-zinc-800 rounded-xl p-4 cursor-pointer hover:bg-zinc-700 transition-colors border border-zinc-700 hover:border-blue-500 text-sm text-zinc-300"
    >
      {question}
    </div>
  )
}
