export default function QueryCounter({ queriesRemaining, resetAt, tierLimit = 3 }) {
  if (queriesRemaining === null || queriesRemaining === undefined) return null

  function formatResetTime(iso) {
    if (!iso) return ''
    const d = new Date(iso)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  let colorClass = 'text-zinc-400'
  if (queriesRemaining === 0) {
    colorClass = 'text-red-400'
  } else if (queriesRemaining <= 2) {
    colorClass = 'text-amber-400'
  }

  return (
    <span aria-live="polite" className={`text-xs ${colorClass}`}>
      {queriesRemaining === 0
        ? `Daily limit reached. Resets at ${formatResetTime(resetAt)}.`
        : `${queriesRemaining} of ${tierLimit} queries remaining today`}
    </span>
  )
}
