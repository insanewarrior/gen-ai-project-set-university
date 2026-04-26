const PERSONAL_STYLE = {
  borderLeft: '3px solid #60a5fa',
  background: 'rgba(96,165,250,0.08)',
  borderRadius: '0 6px 6px 0',
}

const KNOWLEDGE_STYLE = {
  borderLeft: '3px solid #fbbf24',
  background: 'rgba(251,191,36,0.08)',
  borderRadius: '0 6px 6px 0',
}

export default function CitationBlock({ type, citation }) {
  if (type === 'personal') {
    return (
      <div style={PERSONAL_STYLE} className="p-3 mb-2 text-sm text-zinc-300" aria-label="Personal training data citation">
        <span className="text-xs font-bold uppercase text-blue-400">YOUR DATA</span>
        <p className="mt-1">{citation.sessionDate} — {citation.exercise}: {citation.detail}</p>
      </div>
    )
  }

  return (
    <div style={KNOWLEDGE_STYLE} className="p-3 mb-2 text-sm text-zinc-300" aria-label="General knowledge citation">
      <span className="text-xs font-bold uppercase text-amber-400">TRAINING SCIENCE</span>
      <p className="mt-1">{citation.principle} — {citation.doc_title || citation.source}</p>
    </div>
  )
}
