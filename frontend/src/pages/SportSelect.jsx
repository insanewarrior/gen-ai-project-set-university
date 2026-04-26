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
        console.warn('Failed to save sport attribute:', result.error)
      }
    }
    setLoading(false)
    onSuccess?.()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-[400px]">
        <div className="text-center mb-8">
          <span className="text-accent font-black italic text-4xl">S</span>
          <p className="text-text-muted text-sm mt-2 tracking-wide uppercase">StrengthWise</p>
        </div>
        <div className="bg-surface border border-border rounded-2xl p-6">
          <h1 className="text-xl font-bold text-white mb-2">What do you train?</h1>
          <p className="text-text-muted text-sm mb-6">
            We&apos;ll personalize your experience based on your sport.
          </p>
          {error && <p className="text-error text-sm mb-4">{error}</p>}
          <div className="flex flex-col gap-2">
            {SPORTS.map((sport) => (
              <button
                key={sport}
                disabled={loading}
                onClick={() => handleSelect(sport)}
                className={`w-full min-h-[48px] rounded-lg border text-left px-4 font-medium text-sm transition-all disabled:opacity-50 ${
                  selected === sport
                    ? 'bg-[#b8ff3c18] border-accent text-accent'
                    : 'bg-surface-2 border-border text-text-secondary hover:border-[#b8ff3c33] hover:text-white'
                }`}
              >
                {sport}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
