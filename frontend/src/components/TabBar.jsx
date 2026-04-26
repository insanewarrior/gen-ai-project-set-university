import { NavLink } from 'react-router-dom'
import { Home, PenLine, MessageCircle, BarChart2, User } from 'lucide-react'

const NAV_ITEMS = [
  { to: '/', label: 'Home', Icon: Home },
  { to: '/log', label: 'Log', Icon: PenLine },
  { to: '/chat', label: 'Chat', Icon: MessageCircle },
  { to: '/history', label: 'History', Icon: BarChart2 },
]

export default function TabBar({ mobile }) {
  if (mobile) {
    return (
      <nav className="md:hidden flex justify-around items-center h-14 bg-[#0d0d0d] border-t border-[#1e1e1e]">
        {NAV_ITEMS.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center min-w-[44px] min-h-[44px] gap-0.5 text-[10px] font-medium transition-colors ${
                isActive ? 'text-accent' : 'text-tab-inactive'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={20} strokeWidth={isActive ? 2.5 : 1.8} />
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    )
  }

  return (
    <nav className="hidden md:flex flex-col items-center w-16 bg-[#0d0d0d] border-r border-[#1e1e1e] py-4 gap-1 shrink-0">
      {/* Logo monogram */}
      <span className="text-accent font-black italic text-xl mb-4 select-none">S</span>

      {NAV_ITEMS.map(({ to, label, Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          title={label}
          className={({ isActive }) =>
            `w-11 h-11 flex items-center justify-center rounded-xl transition-colors ${
              isActive
                ? 'bg-[#b8ff3c18] border border-[#b8ff3c33] text-accent'
                : 'text-[#444] hover:text-[#777]'
            }`
          }
        >
          {({ isActive }) => (
            <Icon size={20} strokeWidth={isActive ? 2.5 : 1.8} />
          )}
        </NavLink>
      ))}

      {/* Profile pinned to bottom */}
      <NavLink
        to="/profile"
        title="Profile"
        className={({ isActive }) =>
          `w-11 h-11 flex items-center justify-center rounded-xl mt-auto transition-colors ${
            isActive
              ? 'bg-[#b8ff3c18] border border-[#b8ff3c33] text-accent'
              : 'text-[#444] hover:text-[#777]'
          }`
        }
      >
        {({ isActive }) => (
          <User size={20} strokeWidth={isActive ? 2.5 : 1.8} />
        )}
      </NavLink>
    </nav>
  )
}
