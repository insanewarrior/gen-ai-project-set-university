import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getSessions, getSession } from '../api'
import SessionCard from '../components/SessionCard'
import { formatDate } from '../components/sessionUtils'
import SessionDetail from '../components/SessionDetail'

function groupByDate(sessions) {
  const groups = new Map()
  sessions.forEach((s) => {
    const date = s.sessionDate
    if (!groups.has(date)) groups.set(date, [])
    groups.get(date).push(s)
  })
  return groups
}

export default function History() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedSession, setSelectedSession] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const result = await getSessions()
        setSessions(result.data.sessions || [])
      } catch {
        setError('Failed to load sessions.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Detail view
  if (selectedSession) {
    return (
      <SessionDetail
        session={selectedSession}
        onBack={() => setSelectedSession(null)}
      />
    )
  }

  // Loading state
  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">History</h1>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-zinc-800 rounded h-12 mb-2 animate-pulse" />
        ))}
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">History</h1>
        <p className="text-red-400">{error}</p>
      </div>
    )
  }

  // Empty state
  if (sessions.length === 0) {
    return (
      <div className="text-center mt-12">
        <p className="text-zinc-400 mb-4">No sessions logged yet.</p>
        <Link
          to="/log"
          className="bg-blue-500 text-white px-6 py-3 rounded-lg font-medium inline-block"
        >
          Log Session
        </Link>
      </div>
    )
  }

  // Session list view
  const dateGroups = groupByDate(sessions)

  async function handleSessionClick(session) {
    try {
      const result = await getSession(session.sessionId, session.sessionDate)
      setSelectedSession(result.data.session)
    } catch {
      setError('Failed to load session details.')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">History</h1>
      <div role="list">
        {[...dateGroups.entries()].map(([date, dateSessions]) => (
          <div key={date}>
            <h2 className="text-zinc-500 text-xs uppercase font-semibold tracking-wider mb-1 mt-4">
              {formatDate(date)}
            </h2>
            {dateSessions.map((session) => (
              <div key={session.sessionId} role="listitem">
                <SessionCard
                  session={session}
                  variant="history"
                  onClick={() => handleSessionClick(session)}
                />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
