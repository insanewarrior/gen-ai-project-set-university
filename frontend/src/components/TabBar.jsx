import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Home', icon: '🏠' },
  { to: '/log', label: 'Log', icon: '📝' },
  { to: '/chat', label: 'Chat', icon: '💬' },
  { to: '/history', label: 'History', icon: '📊' },
]

function NavItem({ to, label, icon }) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        `flex flex-col items-center justify-center min-w-[44px] min-h-[44px] gap-0.5 text-xs ${
          isActive ? 'text-accent-action' : 'text-tab-inactive'
        }`
      }
    >
      <span className="text-lg">{icon}</span>
      <span>{label}</span>
    </NavLink>
  )
}

export default function TabBar({ mobile }) {
  if (mobile) {
    return (
      <nav className="md:hidden flex justify-around items-center h-14 bg-surface border-t border-zinc-700">
        {NAV_ITEMS.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
      </nav>
    )
  }

  return (
    <nav className="hidden md:flex flex-col gap-1 w-[200px] bg-surface p-3 border-r border-zinc-700">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-2 rounded min-h-[44px] ${
              isActive ? 'text-accent-action bg-zinc-800' : 'text-tab-inactive hover:text-zinc-300'
            }`
          }
        >
          <span>{item.icon}</span>
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
