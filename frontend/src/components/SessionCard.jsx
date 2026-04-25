import { SPORT_LABELS, formatDate } from './sessionUtils'

export default function SessionCard({ session, variant, onClick }) {
  const exerciseCount = session.exercises?.length || 0
  const totalSets = session.exercises?.reduce((sum, ex) => sum + (ex.sets?.length || 0), 0) || 0
  const sportLabel = SPORT_LABELS[session.sport] || session.sport
  const dateLabel = formatDate(session.sessionDate)

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') onClick?.()
  }

  if (variant === 'dashboard') {
    return (
      <div
        role="article"
        aria-label={`Training session: ${dateLabel} - ${sportLabel}`}
        tabIndex={0}
        onClick={onClick}
        onKeyDown={handleKeyDown}
        className="bg-zinc-800 rounded-lg p-3 cursor-pointer hover:bg-zinc-700 min-h-[44px]"
      >
        <div className="flex items-center justify-between mb-1">
          <span className="text-zinc-100 text-sm">{dateLabel}</span>
          <span className="text-zinc-400 text-xs">{sportLabel}</span>
        </div>
        <div className="flex items-center gap-3 text-zinc-400 text-sm">
          <span>{exerciseCount} exercises</span>
          <span>{totalSets} sets</span>
        </div>
      </div>
    )
  }

  // History variant
  return (
    <div
      role="article"
      aria-label={`Training session: ${dateLabel} - ${sportLabel}`}
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      className="bg-transparent border-b border-zinc-800 py-3 px-0 cursor-pointer hover:bg-zinc-800/50 min-h-[44px] flex items-center justify-between"
    >
      <div className="flex items-center gap-2">
        <span className="text-zinc-100 text-sm">{dateLabel}</span>
        <span className="text-zinc-500 text-xs">{sportLabel}</span>
      </div>
      <span className="font-mono text-zinc-400 text-sm">{totalSets} sets</span>
    </div>
  )
}
