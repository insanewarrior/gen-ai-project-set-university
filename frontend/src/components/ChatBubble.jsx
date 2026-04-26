import CitationBlock from './CitationBlock'
import FeedbackButtons from './FeedbackButtons'
import FollowupChip from './FollowupChip'

export default function ChatBubble({ role, message, citations, followups, onFollowupSelect, queryId }) {
  if (role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-blue-500 text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-[90%] md:max-w-[70%] text-sm">
          {message}
        </div>
      </div>
    )
  }

  const personalCitations = citations?.personal ?? []
  const knowledgeCitations = citations?.knowledge ?? []

  return (
    <div className="flex flex-col gap-2 max-w-full">
      <div className="bg-zinc-800 text-zinc-100 rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed">
        <p>{message}</p>
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
