import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCurrentUser, updateSport } from '../auth'

const SPORTS = ['Grip Sport', 'Armwrestling', 'Powerlifting', 'General Strength']

export default function SportSelect({ onSuccess }) {
  const navigate = useNavigate()
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSelect(sport) {
    setSelected(sport)
    setError('')
    setLoading(true)
    const cognitoUser = getCurrentUser()
    if (cognitoUser) {
      const result = await updateSport(cognitoUser, sport)
      if (!result.success) {
        // Non-blocking — sport attribute is best-effort for MVP
        console.warn('Failed to save sport attribute:', result.error)
      }
    }
    setLoading(false)
    onSuccess?.()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-zinc-900 flex items-center justify-center p-4">
      <div className="w-full max-w-[400px] bg-zinc-800 rounded-[8px] p-6">
        <h1 className="text-xl font-semibold text-white mb-2">
          What do you train?
        </h1>
        <p className="text-zinc-400 text-sm mb-6">
          We&apos;ll personalize your experience based on your sport.
        </p>
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
        <div className="flex flex-col gap-3">
          {SPORTS.map((sport) => (
            <button
              key={sport}
              disabled={loading}
              onClick={() => handleSelect(sport)}
              className={`w-full min-h-[48px] rounded-[6px] border text-left px-4 font-medium transition-colors disabled:opacity-50 ${
                selected === sport
                  ? 'bg-blue-500 border-blue-500 text-white'
                  : 'bg-zinc-800 border-zinc-700 text-zinc-200 hover:border-blue-400 hover:text-white'
              }`}
            >
              {sport}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
