import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import SportSelector, {
  getSavedSport,
  saveSport,
} from '../components/SportSelector'
import ExercisePicker from '../components/ExercisePicker'
import ExerciseBlock from '../components/ExerciseBlock'
import { createSession, getSessions } from '../api'

function buildHint(sets) {
  if (!sets?.length) return null
  const { weight, reps } = sets[0]
  if (weight != null && reps != null)
    return `Last: ${sets.length}x${reps} @ ${weight}kg`
  if (reps != null) return `Last: ${sets.length}x${reps}`
  return null
}

export default function LogSession() {
  const [date, setDate] = useState(
    () => new Date().toISOString().split('T')[0]
  )
  const [sport, setSport] = useState(getSavedSport() || 'grip')
  const [exerciseBlocks, setExerciseBlocks] = useState([])
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveResult, setSaveResult] = useState(null)
  const [saveError, setSaveError] = useState(null)
  const [exerciseHistory, setExerciseHistory] = useState({})

  useEffect(() => {
    getSessions()
      .then((data) => {
        const sessions = data?.data?.sessions || []
        const map = {}
        sessions.forEach((session) => {
          ;(session.exercises || []).forEach((ex) => {
            const id = ex.exerciseId
            if (!map[id]) {
              map[id] = ex.sets || []
            }
          })
        })
        setExerciseHistory(map)
      })
      .catch(() => {})
  }, [])

  function handleSportChange(key) {
    setSport(key)
    saveSport(key)
    setExerciseBlocks([])
  }

  function handleAddExercise(exercise) {
    const id = exercise.id
    if (exerciseBlocks.some((b) => b.exercise.id === id)) return
    const historySets = exerciseHistory[id] || []
    const hint = buildHint(historySets)
    const initialSets = historySets.length
      ? historySets
      : [{ setNumber: 1, weight: null, reps: null, rpe: null }]
    setExerciseBlocks((prev) => [
      ...prev,
      { exercise, sets: initialSets, hint },
    ])
  }

  function handleBlockChange(exerciseId, sets) {
    setExerciseBlocks((prev) =>
      prev.map((b) =>
        (b.exercise.id || b.exercise.exerciseId) === exerciseId
          ? { ...b, sets }
          : b
      )
    )
  }

  function handleRemove(exerciseId) {
    setExerciseBlocks((prev) =>
      prev.filter(
        (b) => (b.exercise.id || b.exercise.exerciseId) !== exerciseId
      )
    )
  }

  async function handleSave() {
    if (exerciseBlocks.length === 0) {
      setSaveError('Add at least one exercise before saving.')
      return
    }
    setSaving(true)
    setSaveError(null)
    try {
      const payload = {
        sessionDate: date,
        sport,
        exercises: exerciseBlocks.map((b) => ({
          exerciseId: b.exercise.id,
          exerciseName: b.exercise.name,
          sportType: b.exercise.sportType,
          sets: b.sets.filter((s) => s.reps != null),
        })),
        notes: notes || null,
      }
      const result = await createSession(payload)
      setSaveResult({ monthCount: result.data.monthCount })
      setExerciseBlocks([])
      setNotes('')
    } catch {
      setSaveError('Failed to save session. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h1 className="text-xl font-bold text-white mb-4">Log Session</h1>

      <div className="mb-3">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-white text-sm w-full"
        />
      </div>

      <div className="mb-3">
        <SportSelector value={sport} onChange={handleSportChange} />
      </div>

      <div className="mb-3">
        <ExercisePicker
          sportType={sport}
          onSelect={handleAddExercise}
          selectedExerciseIds={exerciseBlocks.map(
            (b) => b.exercise.id
          )}
        />
      </div>

      <div className="mb-3">
        {exerciseBlocks.map((block) => (
          <ExerciseBlock
            key={block.exercise.id}
            exercise={block.exercise}
            initialSets={block.sets}
            lastSessionHint={block.hint}
            onChange={handleBlockChange}
            onRemove={handleRemove}
          />
        ))}
      </div>

      <div className="mb-3">
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          maxLength={500}
          rows={3}
          className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-2 text-white text-sm resize-none"
          style={{ maxHeight: '120px', overflowY: 'auto' }}
          placeholder="Session notes (optional)"
        />
        <span className="text-zinc-500 text-xs">
          {500 - notes.length} chars remaining
        </span>
      </div>

      {saveError && (
        <p className="text-red-500 text-sm mb-2">{saveError}</p>
      )}

      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg mt-4"
      >
        {saving ? 'Saving…' : 'Save Session'}
      </button>

      {saveResult && (
        <div className="mt-3">
          <p className="text-green-500 text-sm">
            Session saved. {saveResult.monthCount} sessions this month.
          </p>
          <Link
            to="/chat"
            className="text-blue-400 text-sm underline"
          >
            Ask me anything about your training →
          </Link>
        </div>
      )}
    </div>
  )
}
