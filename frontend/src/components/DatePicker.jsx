import { useState, useRef, useEffect } from 'react'
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react'

const DAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

function parseLocal(dateStr) {
  const [y, m, d] = dateStr.split('-').map(Number)
  return new Date(y, m - 1, d)
}

function toDateStr(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export default function DatePicker({ value, onChange }) {
  const selected = parseLocal(value)
  const [open, setOpen] = useState(false)
  const [cursor, setCursor] = useState(
    () => new Date(selected.getFullYear(), selected.getMonth(), 1)
  )
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  function prevMonth() {
    setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))
  }
  function nextMonth() {
    setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))
  }

  function selectDay(day) {
    const picked = new Date(cursor.getFullYear(), cursor.getMonth(), day)
    onChange(toDateStr(picked))
    setOpen(false)
  }

  const today = toDateStr(new Date())
  const firstDow = cursor.getDay()
  const daysInMonth = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0).getDate()
  const cells = Array(firstDow).fill(null).concat(
    Array.from({ length: daysInMonth }, (_, i) => i + 1)
  )
  while (cells.length % 7 !== 0) cells.push(null)

  const monthLabel = cursor.toLocaleString('default', { month: 'long', year: 'numeric' })

  return (
    <div className="relative flex gap-2" ref={ref}>
      <input
        type="date"
        value={value}
        onChange={(e) => {
          onChange(e.target.value)
          if (e.target.value) {
            const d = parseLocal(e.target.value)
            setCursor(new Date(d.getFullYear(), d.getMonth(), 1))
          }
        }}
        className="flex-1 bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-accent transition-colors"
      />
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-text-muted hover:text-white hover:border-accent transition-colors"
        aria-label="Open calendar"
      >
        <Calendar size={16} />
      </button>

      {open && (
        <div className="absolute top-full mt-1 right-0 z-50 bg-surface-2 border border-border rounded-xl p-3 shadow-xl w-64">
          <div className="flex items-center justify-between mb-2">
            <button
              type="button"
              onClick={prevMonth}
              className="p-1 rounded hover:bg-surface-3 text-text-muted hover:text-white transition-colors"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="text-white text-sm font-semibold">{monthLabel}</span>
            <button
              type="button"
              onClick={nextMonth}
              className="p-1 rounded hover:bg-surface-3 text-text-muted hover:text-white transition-colors"
            >
              <ChevronRight size={16} />
            </button>
          </div>

          <div className="grid grid-cols-7 mb-1">
            {DAYS.map((d) => (
              <span key={d} className="text-center text-text-muted text-xs py-1">
                {d}
              </span>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-y-0.5">
            {cells.map((day, i) => {
              if (!day) return <span key={i} />
              const cellStr = toDateStr(
                new Date(cursor.getFullYear(), cursor.getMonth(), day)
              )
              const isSelected = cellStr === value
              const isToday = cellStr === today
              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => selectDay(day)}
                  className={[
                    'text-xs rounded py-1 font-medium transition-colors',
                    isSelected
                      ? 'bg-accent text-black'
                      : isToday
                      ? 'bg-surface-3 text-accent'
                      : 'text-white hover:bg-surface-3',
                  ].join(' ')}
                >
                  {day}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
