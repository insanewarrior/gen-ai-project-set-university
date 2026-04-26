import ReactMarkdown from 'react-markdown'
import CitationBlock from './CitationBlock'
import FeedbackButtons from './FeedbackButtons'
import FollowupChip from './FollowupChip'

const MD_COMPONENTS = {
  h1: ({ children }) => <h3 className="text-base font-semibold mt-3 mb-1">{children}</h3>,
  h2: ({ children }) => <h3 className="text-base font-semibold mt-3 mb-1">{children}</h3>,
  h3: ({ children }) => <h4 className="text-sm font-semibold mt-3 mb-1 text-white">{children}</h4>,
  h4: ({ children }) => <h5 className="text-sm font-semibold mt-2 mb-1 text-white">{children}</h5>,
  p:  ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-0.5">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-0.5">{children}</ol>,
  li: ({ children }) => <li>{children}</li>,
  strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  code: ({ children }) => <code className="px-1 py-0.5 rounded bg-[#1e1e1e] text-accent text-xs">{children}</code>,
  table: ({ children }) => <table className="my-2 text-xs border-collapse">{children}</table>,
  th: ({ children }) => <th className="border border-border px-2 py-1 text-left">{children}</th>,
  td: ({ children }) => <td className="border border-border-subtle px-2 py-1">{children}</td>,
}

export default function ChatBubble({ role, message, citations, followups, onFollowupSelect, queryId }) {
  if (role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-[#1a1a1a] text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-[90%] md:max-w-[70%] text-sm border border-border">
          {message}
        </div>
      </div>
    )
  }

  const personalCitations = citations?.personal ?? []
  const knowledgeCitations = citations?.knowledge ?? []

  return (
    <div className="flex flex-col gap-2 max-w-full">
      <div className="bg-surface text-white rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed border-l-4 border-accent">
        <ReactMarkdown components={MD_COMPONENTS}>{message}</ReactMarkdown>
        {personalCitations.map((c, i) => (
          <CitationBlock key={i} type="personal" citation={c} />
        ))}
        {knowledgeCitations.map((c, i) => (
          <CitationBlock key={i} type="knowledge" citation={c} />
        ))}
        <p className="text-xs text-zinc-500 italic px-1 mt-2">StrengthWise provides training insights, not medical advice.</p>
      </div>
      {followups && followups.length > 0 && (
        <div className="flex flex-wrap gap-2 px-1">
          {followups.map((q, i) => (
            <FollowupChip key={i} question={q} onSelect={onFollowupSelect} />
          ))}
        </div>
      )}
      <FeedbackButtons queryId={queryId} />
    </div>
  )
}
