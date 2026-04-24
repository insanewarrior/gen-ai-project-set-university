export default function HeaderBar({ title, onSignOut }) {
  return (
    <header className="h-12 flex items-center justify-between px-4 bg-surface border-b border-zinc-700">
      <h1 className="text-base font-semibold text-zinc-100">{title}</h1>
      {onSignOut && (
        <button
          onClick={onSignOut}
          className="text-sm text-zinc-400 hover:text-zinc-200 px-3 py-1 rounded border border-zinc-700 hover:border-zinc-500 transition-colors"
        >
          Sign Out
        </button>
      )}
    </header>
  )
}
