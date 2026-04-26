import { useState, useEffect } from 'react'
import { getProfile, exportTrainingData, deleteAccount } from '../api'
import { signOut } from '../auth'
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
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState(null)

  async function handleDeleteAccount() {
    setDeleting(true)
    setDeleteError(null)
    try {
      await deleteAccount()
      signOut()
      window.location.href = '/login'
    } catch {
      setDeleteError('Account deletion failed. Please try again.')
      setDeleting(false)
    }
  }

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
      <div className="bg-zinc-800 rounded-lg px-4 py-3 mt-4">
        <p className="text-zinc-400 text-xs mb-2">Danger zone</p>
        {!showDeleteConfirm ? (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="w-full py-2 px-4 text-red-400 rounded-lg text-sm hover:bg-red-500/10 transition-colors"
          >
            Delete Account
          </button>
        ) : (
          <div>
            <p className="text-zinc-300 text-sm mb-3">
              Delete your account and all training data? This cannot be undone.
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleDeleteAccount}
                disabled={deleting}
                className="flex-1 py-2 px-4 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </button>
              <button
                onClick={() => { setShowDeleteConfirm(false); setDeleteError(null) }}
                disabled={deleting}
                className="flex-1 py-2 px-4 text-zinc-400 rounded-lg text-sm hover:bg-zinc-700 disabled:opacity-50 transition-colors"
              >
                Cancel
              </button>
            </div>
            {deleteError && <p className="text-red-400 text-xs mt-2">{deleteError}</p>}
          </div>
        )}
      </div>
    </div>
  )
}
