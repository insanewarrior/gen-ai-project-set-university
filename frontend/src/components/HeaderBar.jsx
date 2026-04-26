import { NavLink } from 'react-router-dom'
import { User, LogOut } from 'lucide-react'

export default function HeaderBar({ title, onSignOut }) {
  return (
    <header className="h-12 flex items-center justify-between px-4 bg-[#0d0d0d] border-b border-[#1e1e1e]">
      <h1 className="text-sm font-semibold text-[#555] tracking-wide">{title}</h1>
      <div className="flex items-center gap-2">
        <NavLink
          to="/profile"
          title="Profile & Usage"
          className={({ isActive }) =>
            `flex items-center justify-center w-10 h-10 rounded-full border transition-colors ${
              isActive
                ? 'border-accent text-accent'
                : 'border-[#3a3a3a] text-[#aaa] hover:border-[#555] hover:text-white'
            }`
          }
        >
          <User size={18} strokeWidth={1.8} />
        </NavLink>
        {onSignOut && (
          <button
            onClick={onSignOut}
            title="Sign out"
            className="flex items-center gap-1.5 text-sm text-[#aaa] hover:text-white px-3 py-2 rounded border border-[#3a3a3a] hover:border-[#555] transition-colors"
          >
            <LogOut size={15} strokeWidth={1.8} />
            <span>Sign Out</span>
          </button>
        )}
      </div>
    </header>
  )
}
