import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { signIn } from '../auth'

export default function SignIn({ onSuccess }) {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    const result = await signIn(email, password)
    setLoading(false)
    if (result.success) {
      onSuccess?.()
      navigate('/')
    } else {
      setError(result.error || 'Sign in failed. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-zinc-900 flex items-center justify-center p-4">
      <div className="w-full max-w-[400px] bg-zinc-800 rounded-[8px] p-6">
        <h1 className="text-xl font-semibold text-white mb-6">Sign In</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm text-zinc-400" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-zinc-800 border border-zinc-700 rounded-[6px] px-3 py-2 text-[16px] text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm text-zinc-400" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-zinc-800 border border-zinc-700 rounded-[6px] px-3 py-2 text-[16px] text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          {error && (
            <p className="text-red-400 text-sm">{error}</p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white font-medium rounded-[6px] min-h-[44px] w-full mt-2"
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <p className="text-zinc-400 text-sm mt-4 text-center">
          Don&apos;t have an account?{' '}
          <Link to="/signup" className="text-blue-400 hover:underline">
            Create account
          </Link>
        </p>
      </div>
    </div>
  )
}
