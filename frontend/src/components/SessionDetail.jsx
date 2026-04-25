import { SPORT_LABELS, formatDate } from './sessionUtils'

export default function SessionDetail({ session, onBack }) {
  const sportLabel = SPORT_LABELS[session.sport] || session.sport
  const dateLabel = formatDate(session.sessionDate)

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={onBack}
          aria-label="Back to history"
          className="text-zinc-400 hover:text-zinc-100 min-w-[44px] min-h-[44px] flex items-center justify-center"
        >
          <span className="text-xl">&larr;</span>
        </button>
        <div>
          <h2 className="text-zinc-100 text-lg font-semibold">{dateLabel}</h2>
          <span className="text-zinc-400 text-sm">{sportLabel}</span>
        </div>
      </div>

      {/* Exercises */}
      {session.exercises?.map((exercise, idx) => (
        <div key={exercise.exerciseId || idx} className="bg-zinc-800 rounded-lg p-3 mb-2">
          <h3 className="text-zinc-100 font-semibold mb-2">{exercise.exerciseName}</h3>
          {/* Header row */}
          <div className="grid grid-cols-[40px_1fr_1fr_60px] gap-1 text-zinc-500 text-xs mb-1">
            <span>Set</span>
            <span>Weight (kg)</span>
            <span>Reps</span>
            <span>RPE</span>
          </div>
          {/* Set rows */}
          {exercise.sets?.map((set) => (
            <div
              key={set.setNumber}
              className="grid grid-cols-[40px_1fr_1fr_60px] gap-1 font-mono text-zinc-100 text-sm py-1"
            >
              <span className="text-zinc-400">{set.setNumber}</span>
              <span>{set.weight ?? '—'}</span>
              <span>{set.reps ?? '—'}</span>
              <span>{set.rpe != null ? set.rpe : '—'}</span>
            </div>
          ))}
        </div>
      ))}

      {/* Notes */}
      {session.notes && (
        <div className="mt-3">
          <span className="text-zinc-400 text-sm font-medium">Notes:</span>
          <p className="text-zinc-400 text-sm italic mt-1">{session.notes}</p>
        </div>
      )}
    </div>
  )
}
