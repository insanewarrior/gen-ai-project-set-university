import { Outlet, useLocation } from 'react-router-dom'
import HeaderBar from './components/HeaderBar'
import TabBar from './components/TabBar'

const TITLES = {
  '/': 'Home',
  '/log': 'Log Session',
  '/chat': 'Chat',
  '/history': 'History',
}

export default function App() {
  const location = useLocation()
  const title = TITLES[location.pathname] || 'StrengthWise'

  return (
    <div className="flex flex-col min-h-dvh bg-bg">
      <HeaderBar title={title} />
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop sidebar */}
        <TabBar />
        {/* Content area */}
        <main className="flex-1 overflow-y-auto p-4 md:max-w-[720px]">
          <Outlet />
        </main>
      </div>
      {/* Mobile tab bar */}
      <TabBar mobile />
    </div>
  )
}
