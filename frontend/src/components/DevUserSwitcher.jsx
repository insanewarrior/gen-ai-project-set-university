import { useState } from 'react'
import { getDevUser, setDevUser } from '../api'

const USERS = [
  { key: 'free', label: 'Free', color: 'text-zinc-300' },
  { key: 'onboarding', label: 'Onboard', color: 'text-amber-400' },
  { key: 'premium', label: 'Premium', color: 'text-blue-400' },
]

export default function DevUserSwitcher() {
  const [current, setCurrent] = useState(getDevUser)

  function switchUser(key) {
    setDevUser(key)
    setCurrent(key)
    window.location.reload()
  }

  return (
    <div className="fixed bottom-4 left-4 z-50 flex items-center gap-1 bg-zinc-900 border border-zinc-600 rounded-full px-2 py-1 text-xs shadow-lg">
      <span className="text-zinc-500 mr-1">DEV</span>
      {USERS.map(({ key, label, color }) => (
        <button
          key={key}
          onClick={() => switchUser(key)}
          className={`px-2 py-0.5 rounded-full transition-colors ${
            current === key
              ? `${color} bg-zinc-700 font-semibold`
              : 'text-zinc-500 hover:text-zinc-300'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
