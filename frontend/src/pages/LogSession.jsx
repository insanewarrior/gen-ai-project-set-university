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
    <div className="p-4 md:p-6 max-w-2xl mx-auto w-full">
      <h1 className="text-2xl font-black text-white tracking-tight mb-6">Log Session</h1>

      <div className="mb-4">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-white text-sm w-full focus:outline-none focus:border-accent transition-colors"
        />
      </div>

      <div className="mb-4">
        <SportSelector value={sport} onChange={handleSportChange} />
      </div>

      <div className="mb-4">
        <ExercisePicker
          sportType={sport}
          onSelect={handleAddExercise}
          selectedExerciseIds={exerciseBlocks.map(
            (b) => b.exercise.id
          )}
        />
      </div>

      <div className="mb-4">
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

      <div className="mb-4">
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          maxLength={500}
          rows={3}
          className="w-full bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-white text-sm resize-none focus:outline-none focus:border-accent transition-colors"
          style={{ maxHeight: '120px', overflowY: 'auto' }}
          placeholder="Session notes (optional)"
        />
        <span className="text-text-muted text-xs">
          {500 - notes.length} chars remaining
        </span>
      </div>

      {saveError && (
        <p className="text-error text-sm mb-2">{saveError}</p>
      )}

      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full bg-accent hover:brightness-110 disabled:opacity-50 text-black font-bold py-3 rounded-lg mt-2 transition-all"
      >
        {saving ? 'Saving…' : 'Save Session'}
      </button>

      {saveResult && (
        <div className="mt-4">
          <p className="text-success text-sm">
            Session saved. {saveResult.monthCount} sessions this month.
          </p>
          <Link
            to="/chat"
            className="text-accent text-sm font-medium hover:brightness-110"
          >
            Ask me anything about your training →
          </Link>
        </div>
      )}
    </div>
  )
}
