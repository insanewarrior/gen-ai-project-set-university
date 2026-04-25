export const SPORT_LABELS = {
  grip: 'Grip Sport',
  armwrestling: 'Armwrestling',
  powerlifting: 'Powerlifting',
  general: 'General Strength',
}

export function formatDate(dateStr) {
  const today = new Date().toISOString().slice(0, 10)
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10)
  if (dateStr === today) return 'Today'
  if (dateStr === yesterday) return 'Yesterday'
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
