import { ArrowLeft } from 'lucide-react'
import { SPORT_LABELS, formatDate } from './sessionUtils'

export default function SessionDetail({ session, onBack }) {
  const sportLabel = SPORT_LABELS[session.sport] || session.sport
  const dateLabel = formatDate(session.sessionDate)

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onBack}
          aria-label="Back to history"
          className="w-9 h-9 flex items-center justify-center rounded-lg text-text-muted hover:text-white hover:bg-surface transition-colors"
        >
          <ArrowLeft size={18} strokeWidth={2} />
        </button>
        <div>
          <h2 className="text-white text-lg font-bold leading-tight">{dateLabel}</h2>
          <span className="text-text-muted text-xs uppercase tracking-widest">{sportLabel}</span>
        </div>
      </div>

      {/* Exercises */}
      {session.exercises?.map((exercise, idx) => (
        <div key={exercise.exerciseId || idx} className="bg-surface border border-border rounded-xl p-4 mb-3">
          <h3 className="text-white font-semibold mb-3 text-sm">{exercise.exerciseName}</h3>
          {/* Header row */}
          <div className="grid grid-cols-[40px_1fr_1fr_60px] gap-1 text-text-muted text-[10px] uppercase tracking-widest mb-2">
            <span>Set</span>
            <span>Weight</span>
            <span>Reps</span>
            <span>RPE</span>
          </div>
          {/* Set rows */}
          {exercise.sets?.map((set) => (
            <div
              key={set.setNumber}
              className="grid grid-cols-[40px_1fr_1fr_60px] gap-1 font-mono text-sm py-1.5 border-t border-border-subtle"
            >
              <span className="text-text-muted">{set.setNumber}</span>
              <span className="text-accent font-semibold">{set.weight ?? '—'}</span>
              <span className="text-accent font-semibold">{set.reps ?? '—'}</span>
              <span className="text-text-secondary">{set.rpe != null ? set.rpe : '—'}</span>
            </div>
          ))}
        </div>
      ))}

      {/* Notes */}
      {session.notes && (
        <div className="mt-4 bg-surface border border-border rounded-xl p-4">
          <span className="text-text-muted text-[10px] uppercase tracking-widest font-semibold block mb-2">Notes</span>
          <p className="text-text-secondary text-sm italic">{session.notes}</p>
        </div>
      )}
    </div>
  )
}
