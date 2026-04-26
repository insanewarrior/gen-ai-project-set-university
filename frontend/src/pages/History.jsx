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
      <div className="p-4 md:p-6 max-w-3xl mx-auto w-full">
        <h1 className="text-2xl font-black text-white tracking-tight mb-6">History</h1>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-surface rounded-xl h-12 mb-2 animate-pulse" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 md:p-6 max-w-3xl mx-auto w-full">
        <h1 className="text-2xl font-black text-white tracking-tight mb-6">History</h1>
        <p className="text-error text-sm">{error}</p>
      </div>
    )
  }

  if (sessions.length === 0) {
    return (
      <div className="p-4 md:p-6 text-center mt-12">
        <p className="text-text-secondary text-sm mb-4">No sessions logged yet.</p>
        <Link
          to="/log"
          className="bg-accent text-black font-bold px-6 py-3 rounded-lg text-sm inline-block hover:brightness-110 transition-all"
        >
          Log Session
        </Link>
      </div>
    )
  }

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
    <div className="p-4 md:p-6 max-w-3xl mx-auto w-full">
      <h1 className="text-2xl font-black text-white tracking-tight mb-6">History</h1>
      <div role="list">
        {[...dateGroups.entries()].map(([date, dateSessions]) => (
          <div key={date}>
            <h2 className="text-text-muted text-[10px] uppercase font-semibold tracking-widest mb-1 mt-5 first:mt-0">
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
