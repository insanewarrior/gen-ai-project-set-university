export default function SetEntryRow({
  setNumber,
  weight,
  reps,
  rpe,
  onChange,
  onEnterLastField,
}) {
  const inputClass =
    'w-full bg-zinc-900 border border-zinc-700 rounded text-center font-mono ' +
    'text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-400 ' +
    'focus:border-blue-500 py-2'

  function handleWeightChange(e) {
    const val = e.target.value
    onChange({ weight: val === '' ? null : parseFloat(val), reps, rpe })
  }

  function handleRepsChange(e) {
    const val = e.target.value
    onChange({ weight, reps: val === '' ? null : parseInt(val, 10), rpe })
  }

  function handleRpeChange(e) {
    const val = e.target.value
    onChange({ weight, reps, rpe: val === '' ? null : parseFloat(val) })
  }

  function handleRpeKeyDown(e) {
    if (e.key === 'Enter') {
      onEnterLastField()
    }
  }

  return (
    <div className="grid grid-cols-[40px_1fr_1fr_60px] gap-1">
      <span className="text-zinc-400 text-sm text-center self-center">
        {setNumber}
      </span>
      <input
        type="text"
        inputMode="decimal"
        placeholder="kg"
        aria-label={`Set ${setNumber} weight`}
        className={inputClass}
        value={weight ?? ''}
        onChange={handleWeightChange}
      />
      <input
        type="text"
        inputMode="numeric"
        placeholder="reps"
        aria-label={`Set ${setNumber} reps`}
        className={inputClass}
        value={reps ?? ''}
        onChange={handleRepsChange}
      />
      <input
        type="text"
        inputMode="decimal"
        placeholder="RPE"
        aria-label={`Set ${setNumber} RPE`}
        className={inputClass}
        value={rpe ?? ''}
        onChange={handleRpeChange}
        onKeyDown={handleRpeKeyDown}
      />
    </div>
  )
}
