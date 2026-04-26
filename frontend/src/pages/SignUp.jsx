import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { signUp, confirmSignUp } from '../auth'

export default function SignUp() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [needsVerification, setNeedsVerification] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSignUp(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    const result = await signUp(email, password)
    setLoading(false)
    if (result.success) {
      setNeedsVerification(true)
    } else {
      setError(result.error || 'Sign up failed. Please try again.')
    }
  }

  async function handleConfirm(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    const result = await confirmSignUp(email, code)
    setLoading(false)
    if (result.success) {
      navigate('/sport-select')
    } else {
      setError(result.error || 'Verification failed. Please try again.')
    }
  }

  const inputClass = 'bg-surface-2 border border-border rounded-lg px-3 py-2.5 text-[16px] text-white w-full focus:outline-none focus:border-accent transition-colors'

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-4">
      <div className="w-full max-w-[400px]">
        <div className="text-center mb-8">
          <span className="text-accent font-black italic text-4xl">S</span>
          <p className="text-text-muted text-sm mt-2 tracking-wide uppercase">StrengthWise</p>
        </div>
        <div className="bg-surface border border-border rounded-2xl p-6">
          <h1 className="text-xl font-bold text-white mb-6">Create Account</h1>

          {!needsVerification ? (
            <form onSubmit={handleSignUp} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-text-muted text-xs uppercase tracking-widest" htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={inputClass}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-text-muted text-xs uppercase tracking-widest" htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={inputClass}
                />
              </div>
              {error && <p className="text-error text-sm">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="bg-accent hover:brightness-110 disabled:opacity-50 text-black font-bold rounded-lg min-h-[44px] w-full mt-2 transition-all"
              >
                {loading ? 'Creating account…' : 'Create Account'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleConfirm} className="flex flex-col gap-4">
              <p className="text-text-secondary text-sm">
                A verification code was sent to <span className="text-white">{email}</span>. Enter it below.
              </p>
              <div className="flex flex-col gap-1.5">
                <label className="text-text-muted text-xs uppercase tracking-widest" htmlFor="code">Verification Code</label>
                <input
                  id="code"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className={inputClass}
                />
              </div>
              {error && <p className="text-error text-sm">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="bg-accent hover:brightness-110 disabled:opacity-50 text-black font-bold rounded-lg min-h-[44px] w-full mt-2 transition-all"
              >
                {loading ? 'Verifying…' : 'Verify Email'}
              </button>
            </form>
          )}

          <p className="text-text-muted text-sm mt-5 text-center">
            Already have an account?{' '}
            <Link to="/login" className="text-accent font-medium hover:brightness-110">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
