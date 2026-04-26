import { NavLink } from 'react-router-dom'

export default function HeaderBar({ title, onSignOut }) {
  return (
    <header className="h-12 flex items-center justify-between px-4 bg-surface border-b border-zinc-700">
      <h1 className="text-base font-semibold text-zinc-100">{title}</h1>
      <div className="flex items-center gap-2">
        <NavLink
          to="/profile"
          title="Profile & Usage"
          className={({ isActive }) =>
            `flex items-center justify-center w-8 h-8 rounded-full border transition-colors ${
              isActive
                ? 'border-blue-500 text-blue-400'
                : 'border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200'
            }`
          }
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path d="M10 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM3.465 14.493a1.23 1.23 0 0 0 .41 1.412A9.957 9.957 0 0 0 10 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 0 0-13.074.003Z" />
          </svg>
        </NavLink>
        {onSignOut && (
          <button
            onClick={onSignOut}
            className="text-sm text-zinc-400 hover:text-zinc-200 px-3 py-1 rounded border border-zinc-700 hover:border-zinc-500 transition-colors"
          >
            Sign Out
          </button>
        )}
      </div>
    </header>
  )
}
