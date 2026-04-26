const PERSONAL_STYLE = {
  borderLeft: '3px solid #00aaff',
  background: 'rgba(0,170,255,0.06)',
  borderRadius: '0 6px 6px 0',
}

const KNOWLEDGE_STYLE = {
  borderLeft: '3px solid #bf00ff',
  background: 'rgba(191,0,255,0.06)',
  borderRadius: '0 6px 6px 0',
}

export default function CitationBlock({ type, citation }) {
  if (type === 'personal') {
    return (
      <div style={PERSONAL_STYLE} className="p-3 mb-2 text-sm text-zinc-300" aria-label="Personal training data citation">
        <span
          className="inline-block text-[10px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded mb-1"
          style={{ background: 'rgba(0,170,255,0.15)', color: '#00aaff' }}
        >
          YOUR DATA
        </span>
        <p className="mt-1">{citation.sessionDate} — {citation.exercise}: {citation.detail}</p>
      </div>
    )
  }

  return (
    <div style={KNOWLEDGE_STYLE} className="p-3 mb-2 text-sm text-zinc-300" aria-label="General knowledge citation">
      <span
        className="inline-block text-[10px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded mb-1"
        style={{ background: 'rgba(191,0,255,0.15)', color: '#bf00ff' }}
      >
        TRAINING SCIENCE
      </span>
      <p className="mt-1">{citation.principle} — {citation.doc_title || citation.source}</p>
    </div>
  )
}
