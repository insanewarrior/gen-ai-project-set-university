import { useState } from 'react'
import SetEntryRow from './SetEntryRow'

export default function ExerciseBlock({
  exercise,
  initialSets,
  lastSessionHint,
  onChange,
  onRemove,
}) {
  const [sets, setSets] = useState(
    initialSets?.length
      ? initialSets
      : [{ setNumber: 1, weight: null, reps: null, rpe: null }]
  )

  function addSet() {
    const last = sets[sets.length - 1]
    const newSet = {
      setNumber: sets.length + 1,
      weight: last.weight,
      reps: last.reps,
      rpe: last.rpe,
    }
    const updated = [...sets, newSet]
    setSets(updated)
    onChange(exercise.exerciseId || exercise.id, updated)
  }

  function handleSetChange(index, values) {
    const updated = sets.map((s, i) =>
      i === index ? { ...s, ...values } : s
    )
    setSets(updated)
    onChange(exercise.exerciseId || exercise.id, updated)
  }

  return (
    <div className="bg-surface border border-border rounded-xl p-3 mb-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-white font-semibold text-sm">{exercise.name}</span>
        <button
          onClick={() => onRemove(exercise.exerciseId || exercise.id)}
          className="text-text-muted hover:text-error text-lg leading-none transition-colors"
          aria-label={`Remove ${exercise.name}`}
        >
          ×
        </button>
      </div>
      {lastSessionHint && (
        <p className="text-text-muted text-xs mb-2">{lastSessionHint}</p>
      )}
      <div className="grid grid-cols-[40px_1fr_1fr_60px] gap-1 text-text-muted text-xs uppercase px-0 mb-1">
        <span className="text-center">Set</span>
        <span className="text-center">Weight</span>
        <span className="text-center">Reps</span>
        <span className="text-center">RPE</span>
      </div>
      {sets.map((set, index) => (
        <SetEntryRow
          key={set.setNumber}
          setNumber={set.setNumber}
          weight={set.weight}
          reps={set.reps}
          rpe={set.rpe}
          onChange={(values) => handleSetChange(index, values)}
          onEnterLastField={
            index === sets.length - 1 ? addSet : undefined
          }
        />
      ))}
      <button
        onClick={addSet}
        className="text-accent text-sm font-medium hover:brightness-110 py-2 w-full text-left transition-all"
      >
        + Add Set
      </button>
    </div>
  )
}
