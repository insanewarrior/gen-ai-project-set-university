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
    <div className="flex justify-between items-center py-3 border-b border-border-subtle last:border-0">
      <span className="text-zinc-400 text-sm">{label}</span>
      <span className="text-white font-medium text-sm">{value}</span>
    </div>
  )
}

function SectionLabel({ children }) {
  return (
    <p className="text-zinc-400 text-[10px] uppercase tracking-widest font-semibold mb-3">{children}</p>
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
      <div className="p-4 md:p-6 flex flex-col gap-3 mt-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-surface rounded-xl h-10 animate-pulse" />
        ))}
      </div>
    )
  }

  if (error) {
    return <p className="text-error text-sm mt-4 p-4">{error}</p>
  }

  return (
    <div className="p-4 md:p-6 max-w-2xl mx-auto w-full">
      <h1 className="text-2xl font-black text-white tracking-tight mb-6">Profile</h1>

      {/* Stats */}
      <div className="mb-6">
        <SectionLabel>Account</SectionLabel>
        <div className="bg-surface border border-border rounded-xl px-4">
          <StatRow label="Sessions logged" value={profile.totalSessions} />
          <StatRow label="Queries made" value={profile.totalQueries} />
          <StatRow label="Account tier" value={TIER_LABELS[profile.tier] ?? profile.tier} />
          <StatRow label="Member since" value={formatDate(profile.accountCreatedAt)} />
        </div>
      </div>

      {/* Query budget */}
      <div className="mb-6">
        <SectionLabel>Today's query budget</SectionLabel>
        <div className="bg-surface border border-border rounded-xl px-4 py-3">
          {profile.queriesRemainingToday === -1
            ? <span className="text-xs text-zinc-400">Unlimited daily queries (Premium)</span>
            : <QueryCounter queriesRemaining={profile.queriesRemainingToday} tierLimit={profile.tierLimit} />
          }
        </div>
      </div>

      {/* Data export */}
      <div className="mb-6">
        <SectionLabel>Your data</SectionLabel>
        <div className="bg-surface border border-border rounded-xl px-4 py-3">
          <button
            onClick={handleExport}
            disabled={exporting}
            className="w-full py-2 px-4 border border-accent text-accent rounded-lg text-sm font-medium hover:bg-[#b8ff3c18] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {exporting ? 'Preparing your export...' : 'Export Training Data (CSV)'}
          </button>
          {exportError && <p className="text-error text-xs mt-2">{exportError}</p>}
        </div>
      </div>

      {/* Danger zone */}
      <div>
        <SectionLabel>Danger zone</SectionLabel>
        <div className="bg-surface border border-border rounded-xl px-4 py-3">
          {!showDeleteConfirm ? (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="w-full py-2 px-4 text-error rounded-lg text-sm hover:bg-error/10 transition-colors"
            >
              Delete Account
            </button>
          ) : (
            <div>
              <p className="text-text-secondary text-sm mb-4">
                Delete your account and all training data? This cannot be undone.
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleDeleteAccount}
                  disabled={deleting}
                  className="flex-1 py-2 px-4 bg-error text-white rounded-lg text-sm font-semibold hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {deleting ? 'Deleting...' : 'Delete'}
                </button>
                <button
                  onClick={() => { setShowDeleteConfirm(false); setDeleteError(null) }}
                  disabled={deleting}
                  className="flex-1 py-2 px-4 text-zinc-400 rounded-lg text-sm hover:bg-surface-2 disabled:opacity-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
              {deleteError && <p className="text-error text-xs mt-2">{deleteError}</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
