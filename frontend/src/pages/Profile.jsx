import { useState, useEffect } from 'react'
import { getProfile, exportTrainingData } from '../api'
import QueryCounter from '../components/QueryCounter'

const TIER_LABELS = {
  free: 'Free',
  onboarding: 'Onboarding (10/day)',
  premium: 'Premium',
}

function StatRow({ label, value }) {
  return (
    <div className="flex justify-between items-center py-3 border-b border-zinc-700 last:border-0">
      <span className="text-zinc-400 text-sm">{label}</span>
      <span className="text-zinc-100 font-medium">{value}</span>
    </div>
  )
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [exporting, setExporting] = useState(false)
  const [exportError, setExportError] = useState(null)

  async function handleExport() {
    setExporting(true)
    setExportError(null)
    try {
      await exportTrainingData()
    } catch {
      setExportError('Export failed. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  useEffect(() => {
    getProfile()
      .then(res => setProfile(res.data))
      .catch(() => setError('Could not load profile.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col gap-3 mt-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-zinc-800 rounded-lg h-10 animate-pulse" />
        ))}
      </div>
    )
  }

  if (error) {
    return <p className="text-red-400 text-sm mt-4">{error}</p>
  }

  return (
    <div>
      <div className="bg-zinc-800 rounded-lg px-4 mb-6">
        <StatRow label="Sessions logged" value={profile.totalSessions} />
        <StatRow label="Queries made" value={profile.totalQueries} />
        <StatRow label="Account tier" value={TIER_LABELS[profile.tier] ?? profile.tier} />
        <StatRow label="Member since" value={formatDate(profile.accountCreatedAt)} />
      </div>
      <div className="bg-zinc-800 rounded-lg px-4 py-3">
        <p className="text-zinc-400 text-xs mb-1">Today's query budget</p>
        {profile.queriesRemainingToday === -1
          ? <span className="text-xs text-zinc-400">Unlimited daily queries (Premium)</span>
          : <QueryCounter queriesRemaining={profile.queriesRemainingToday} tierLimit={profile.tierLimit} />
        }
      </div>
      <div className="bg-zinc-800 rounded-lg px-4 py-3 mt-4">
        <p className="text-zinc-400 text-xs mb-2">Your data</p>
        <button
          onClick={handleExport}
          disabled={exporting}
          className="w-full py-2 px-4 border border-blue-500 text-blue-400 rounded-lg text-sm hover:bg-blue-500/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {exporting ? 'Preparing your export...' : 'Export Training Data (CSV)'}
        </button>
        {exportError && <p className="text-red-400 text-xs mt-2">{exportError}</p>}
      </div>
    </div>
  )
}
