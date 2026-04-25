import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getSessions } from '../api'
import SessionCard from '../components/SessionCard'

export default function Dashboard() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    async function load() {
      try {
        const result = await getSessions()
        setSessions(result.data.sessions || [])
      } catch {
        // Silently handle — dashboard is non-critical
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Loading state
  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">StrengthWise</h1>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-zinc-800 rounded-lg h-24 mb-3 animate-pulse" />
        ))}
      </div>
    )
  }

  // Empty state — new user
  if (sessions.length === 0) {
    return (
      <div className="text-center mt-12">
        <h1 className="text-2xl font-bold text-zinc-100">Welcome to StrengthWise</h1>
        <p className="text-zinc-400 mt-2">Log your first session to get started.</p>
        <Link
          to="/log"
          className="bg-blue-500 text-white px-6 py-3 rounded-lg font-medium text-center block mt-4 w-full md:w-auto md:inline-block"
        >
          Log Session
        </Link>
        <p className="text-zinc-500 text-sm mt-6">
          Log a few sessions first, then ask me anything.
        </p>
      </div>
    )
  }

  // Returning user
  const recentSessions = sessions.slice(0, 3)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">StrengthWise</h1>

      <h2 className="text-zinc-100 font-semibold mb-3">Recent Sessions</h2>
      <div className="flex flex-col gap-3 mb-4">
        {recentSessions.map((session) => (
          <SessionCard
            key={session.sessionId}
            session={session}
            variant="dashboard"
            onClick={() => navigate('/history')}
          />
        ))}
      </div>

      {sessions.length > 3 && (
        <Link
          to="/history"
          className="text-blue-400 hover:text-blue-300 text-sm mb-4 inline-block"
        >
          View All
        </Link>
      )}

      <Link
        to="/log"
        className="bg-blue-500 text-white px-6 py-3 rounded-lg font-medium text-center block mt-4 w-full md:w-auto md:inline-block"
      >
        Log Session
      </Link>
    </div>
  )
}
