import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { getSessions } from '../api'
import SessionCard from '../components/SessionCard'

function todayLabel() {
  return new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })
}

function computeStreak(sessions) {
  if (!sessions.length) return 0
  const dates = [...new Set(sessions.map((s) => s.sessionDate))].sort().reverse()
  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0]
  if (dates[0] !== today && dates[0] !== yesterday) return 0
  let streak = 1
  for (let i = 1; i < dates.length; i++) {
    const prev = new Date(dates[i - 1])
    const curr = new Date(dates[i])
    const diff = (prev - curr) / 86400000
    if (diff === 1) streak++
    else break
  }
  return streak
}

function thisWeekCount(sessions) {
  const now = new Date()
  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() - now.getDay())
  weekStart.setHours(0, 0, 0, 0)
  return sessions.filter((s) => new Date(s.sessionDate) >= weekStart).length
}

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

  const streak = computeStreak(sessions)
  const weekCount = thisWeekCount(sessions)
  const recentSessions = sessions.slice(0, 3)

  if (loading) {
    return (
      <div className="p-4 md:p-6 max-w-3xl mx-auto w-full">
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="h-7 w-16 bg-surface rounded animate-pulse mb-2" />
            <div className="h-4 w-32 bg-surface rounded animate-pulse" />
          </div>
          <div className="h-9 w-32 bg-surface rounded-lg animate-pulse" />
        </div>
        <div className="grid grid-cols-3 gap-3 mb-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-20 bg-surface rounded-xl animate-pulse" />
          ))}
        </div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-16 bg-surface rounded-xl mb-3 animate-pulse" />
        ))}
      </div>
    )
  }

  if (sessions.length === 0) {
    return (
      <div className="p-4 md:p-6 max-w-3xl mx-auto w-full">
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">Home</h1>
            <p className="text-text-muted text-sm mt-0.5">{todayLabel()}</p>
          </div>
          <Link
            to="/log"
            className="flex items-center gap-1.5 bg-accent text-black font-bold text-sm px-4 py-2 rounded-lg hover:brightness-110 transition-all"
          >
            <Plus size={15} strokeWidth={2.5} />
            Log Session
          </Link>
        </div>
        <div className="text-center mt-16">
          <p className="text-text-secondary text-sm">Log your first session to get started.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto w-full">
      {/* Top bar */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Home</h1>
          <p className="text-text-muted text-sm mt-0.5">{todayLabel()}</p>
        </div>
        <Link
          to="/log"
          className="flex items-center gap-1.5 bg-accent text-black font-bold text-sm px-4 py-2 rounded-lg hover:brightness-110 transition-all"
        >
          <Plus size={15} strokeWidth={2.5} />
          Log Session
        </Link>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-surface border border-border rounded-xl p-4">
          <p className="text-text-muted text-[10px] uppercase tracking-widest mb-2">Sessions</p>
          <p className="text-white text-2xl font-black leading-none">{sessions.length}</p>
        </div>
        <div className="bg-surface border border-border rounded-xl p-4">
          <p className="text-text-muted text-[10px] uppercase tracking-widest mb-2">Streak</p>
          <div className="flex items-baseline gap-1">
            <p className="text-accent text-2xl font-black leading-none">{streak}</p>
            <p className="text-accent text-xs font-bold">days</p>
          </div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-4">
          <p className="text-text-muted text-[10px] uppercase tracking-widest mb-2">This Week</p>
          <p className="text-white text-2xl font-black leading-none">{weekCount}</p>
        </div>
      </div>

      {/* Recent sessions */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-text-muted text-[10px] uppercase tracking-widest font-semibold">Recent Sessions</span>
        {sessions.length > 3 && (
          <Link to="/history" className="text-accent text-xs font-semibold hover:brightness-110">
            View All →
          </Link>
        )}
      </div>

      <div className="flex flex-col gap-2">
        {recentSessions.map((session, idx) => (
          <SessionCard
            key={session.sessionId}
            session={session}
            variant="dashboard"
            isFirst={idx === 0}
            onClick={() => navigate('/history')}
          />
        ))}
      </div>
    </div>
  )
}
