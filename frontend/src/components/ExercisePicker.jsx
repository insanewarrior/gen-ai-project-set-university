import { useEffect, useState } from 'react'
import { getExercises } from '../api'

function getFrequency() {
  try {
    return JSON.parse(localStorage.getItem('sw_exercise_frequency') || '{}')
  } catch {
    return {}
  }
}

function incrementFrequency(exerciseId) {
  const freq = getFrequency()
  freq[exerciseId] = (freq[exerciseId] || 0) + 1
  localStorage.setItem('sw_exercise_frequency', JSON.stringify(freq))
}

function sortByFrequency(exercises, frequency) {
  return [...exercises].sort((a, b) => {
    const freqDiff = (frequency[b.id] || 0) - (frequency[a.id] || 0)
    if (freqDiff !== 0) return freqDiff
    return a.name.localeCompare(b.name)
  })
}

export default function ExercisePicker({ sportType, onSelect, selectedExerciseIds = [] }) {
  const [exercises, setExercises] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!sportType) return

    setLoading(true)
    getExercises(sportType)
      .then((data) => {
        const list = data?.data?.exercises?.[sportType] || []
        const frequency = getFrequency()
        setExercises(sortByFrequency(list, frequency))
      })
      .catch(() => setExercises([]))
      .finally(() => setLoading(false))
  }, [sportType])

  function handleSelect(exercise) {
    incrementFrequency(exercise.id)
    const frequency = getFrequency()
    setExercises((prev) => sortByFrequency(prev, frequency))
    onSelect(exercise)
  }

  if (loading) {
    return (
      <div className="flex flex-col gap-2 p-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-11 rounded bg-surface animate-pulse" />
        ))}
      </div>
    )
  }

  if (exercises.length === 0) {
    return (
      <div className="p-4 text-zinc-400 text-sm text-center">No exercises found.</div>
    )
  }

  return (
    <div className="bg-surface border border-border rounded-lg overflow-y-auto max-h-96">
      {exercises.map((exercise) => {
        const isSelected = selectedExerciseIds.includes(exercise.id)
        return (
          <button
            key={exercise.id}
            onClick={() => handleSelect(exercise)}
            className={`w-full py-3 px-4 text-left text-sm flex items-center justify-between
              border-b border-border-subtle last:border-b-0
              ${isSelected ? 'text-text-muted line-through' : 'text-white hover:bg-surface-2'}
            `}
          >
            <span>{exercise.name}</span>
            {isSelected && (
              <span className="text-accent ml-2 font-bold">✓</span>
            )}
          </button>
        )
      })}
    </div>
  )
}
