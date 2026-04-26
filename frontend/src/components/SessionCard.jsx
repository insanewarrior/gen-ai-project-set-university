import { Activity, ChevronRight } from 'lucide-react'
import { SPORT_LABELS, formatDate } from './sessionUtils'

export default function SessionCard({ session, variant, isFirst, onClick }) {
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
        className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors hover:brightness-110 min-h-[44px] ${
          isFirst
            ? 'bg-surface border border-[#b8ff3c33]'
            : 'bg-surface-2 border border-border-subtle'
        }`}
      >
        {/* Icon box */}
        <div
          className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
            isFirst ? 'bg-[#b8ff3c18]' : 'bg-[#1e1e1e]'
          }`}
        >
          <Activity
            size={16}
            strokeWidth={2}
            className={isFirst ? 'text-accent' : 'text-[#444]'}
          />
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline justify-between gap-2">
            <span className={`text-sm font-semibold truncate ${isFirst ? 'text-white' : 'text-text-secondary'}`}>
              {sportLabel}
            </span>
            <span className="text-[11px] text-text-muted shrink-0">{dateLabel}</span>
          </div>
          <p className={`text-xs mt-0.5 ${isFirst ? 'text-accent font-medium' : 'text-text-muted'}`}>
            {exerciseCount} exercise{exerciseCount !== 1 ? 's' : ''} · {totalSets} set{totalSets !== 1 ? 's' : ''}
          </p>
        </div>

        <ChevronRight
          size={14}
          strokeWidth={2}
          className={isFirst ? 'text-accent shrink-0' : 'text-[#2a2a2a] shrink-0'}
        />
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
      className="flex items-center justify-between py-3 px-1 border-b border-border-subtle cursor-pointer hover:bg-surface-2 min-h-[44px] transition-colors"
    >
      <div className="flex items-center gap-2">
        <span className="text-sm text-white font-medium">{sportLabel}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-accent text-sm font-semibold">{totalSets} sets</span>
        <ChevronRight size={14} strokeWidth={2} className="text-[#333]" />
      </div>
    </div>
  )
}
