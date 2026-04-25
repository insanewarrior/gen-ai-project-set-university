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
    <div className="bg-zinc-800 rounded-lg p-3 mb-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-white font-medium">{exercise.name}</span>
        <button
          onClick={() => onRemove(exercise.exerciseId || exercise.id)}
          className="text-zinc-400 hover:text-red-400 text-lg leading-none"
          aria-label={`Remove ${exercise.name}`}
        >
          ×
        </button>
      </div>
      {lastSessionHint && (
        <p className="text-zinc-500 text-xs mb-2">{lastSessionHint}</p>
      )}
      <div className="grid grid-cols-[40px_1fr_1fr_60px] gap-1 text-zinc-500 text-xs uppercase px-0 mb-1">
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
        className="text-blue-400 text-sm hover:text-blue-300 py-2 w-full text-left"
      >
        ＋ Add Set
      </button>
    </div>
  )
}
