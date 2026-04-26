const SPORTS = [
  { key: 'grip', label: 'Grip Sport' },
  { key: 'armwrestling', label: 'Armwrestling' },
  { key: 'powerlifting', label: 'Powerlifting' },
  { key: 'general', label: 'General Strength' },
]

export function getSavedSport() {
  return localStorage.getItem('sw_last_sport') || null
}

export function saveSport(sportKey) {
  localStorage.setItem('sw_last_sport', sportKey)
}

export default function SportSelector({ value, onChange, disabled = false }) {
  return (
    <div
      role="radiogroup"
      aria-label="Select sport"
      className="flex w-full rounded-lg overflow-hidden border border-border"
    >
      {SPORTS.map((sport) => (
        <button
          key={sport.key}
          role="radio"
          aria-checked={value === sport.key}
          onClick={() => !disabled && onChange(sport.key)}
          disabled={disabled}
          className={`flex-1 py-3 text-sm font-medium text-center transition-colors
            ${
              value === sport.key
                ? 'bg-[#b8ff3c18] border-accent text-accent'
                : 'bg-surface-2 text-text-muted hover:text-text-secondary'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        >
          {sport.label}
        </button>
      ))}
    </div>
  )
}
