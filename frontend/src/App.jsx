import { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation, Outlet } from 'react-router-dom'
import { getCurrentUser, signOut as authSignOut } from './auth'
import HeaderBar from './components/HeaderBar'
import TabBar from './components/TabBar'
import DevUserSwitcher from './components/DevUserSwitcher'
import Dashboard from './pages/Dashboard'
import LogSession from './pages/LogSession'
import Chat from './pages/Chat'
import History from './pages/History'
import Profile from './pages/Profile'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import SportSelect from './pages/SportSelect'

const TITLES = {
  '/': 'Home',
  '/log': 'Log Session',
  '/chat': 'Chat',
  '/history': 'History',
  '/profile': 'Profile',
}

function AuthenticatedShell({ onSignOut }) {
  const location = useLocation()
  const title = TITLES[location.pathname] || 'StrengthWise'

  return (
    <div className="flex flex-col min-h-dvh bg-bg">
      <HeaderBar title={title} onSignOut={onSignOut} />
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop sidebar */}
        <TabBar />
        {/* Content area */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden">
          <Outlet />
        </main>
      </div>
      {/* Mobile tab bar */}
      <TabBar mobile />
      {import.meta.env.DEV && <DevUserSwitcher />}
    </div>
  )
}

export default function App() {
  const [user, setUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)

  useEffect(() => {
    try {
      const currentUser = getCurrentUser()
      console.log('[Auth] getCurrentUser result:', currentUser)
      setUser(currentUser)
    } catch (err) {
      console.error('[Auth] getCurrentUser threw:', err)
    } finally {
      setAuthLoading(false)
    }
  }, [])

  function handleSignOut() {
    authSignOut()
    setUser(null)
  }

  function handleSignInSuccess() {
    setUser(getCurrentUser())
  }

  // Blank dark screen while checking auth state — prevents flash of
  // unauthenticated content
  if (authLoading) {
    return <div className="min-h-screen bg-bg" />
  }

  if (!user) {
    return (
      <Routes>
        <Route
          path="/signup"
          element={<SignUp />}
        />
        <Route
          path="/sport-select"
          element={
            <SportSelect onSuccess={handleSignInSuccess} />
          }
        />
        <Route
          path="*"
          element={<SignIn onSuccess={handleSignInSuccess} />}
        />
      </Routes>
    )
  }

  return (
    <Routes>
      <Route element={<AuthenticatedShell onSignOut={handleSignOut} />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/log" element={<LogSession />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/history" element={<History />} />
        <Route path="/profile" element={<Profile />} />
        {/* Redirect auth routes to home when already signed in */}
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route path="/signup" element={<Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
