import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useFrappeAuth, useFrappeGetCall } from 'frappe-react-sdk'
import Nav from '../components/Nav'

// Customer login — Frappe OAuth ("Continue with Google", etc.) plus an
// email/password fallback. Social providers are served live by
// api/v1.get_login_options, so the buttons appear the moment a Social Login Key
// is configured. Returning customers (account created at payment) sign in with
// the same email and land in their portal.
type Provider = { name: string; label: string; url: string }

export default function Login() {
  const navigate = useNavigate()
  const { login } = useFrappeAuth()
  const { data } = useFrappeGetCall<{ message: { providers: Provider[] } }>(
    'knc.api.v1.get_login_options',
    { redirect_to: '/frontend/portal' },
  )
  const providers: Provider[] = (data?.message?.providers ?? (data as { providers?: Provider[] })?.providers ?? [])

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await login({ username: email, password })
      navigate('/portal')
    } catch {
      setError('Wrong email or password.')
      setBusy(false)
    }
  }

  const inputCls =
    'w-full rounded-xl border border-input-border bg-input-bg px-4 py-3 text-base text-ink outline-none transition-colors duration-150 placeholder:text-input-focus focus:border-input-focus'

  return (
    <>
      <Nav />
      <main className="mx-auto flex min-h-screen max-w-[420px] flex-col justify-center px-5 pb-24 pt-[120px]">
        <h1 className="mb-2 text-3xl font-light tracking-head text-ink">Welcome back.</h1>
        <p className="mb-10 text-sm text-ink-muted">Sign in to your project portal.</p>

        {providers.map((p) => (
          <a
            key={p.name}
            href={p.url}
            className="mb-3 flex items-center justify-center rounded-xl border border-line bg-surface-1 py-3 text-sm font-medium text-ink transition-colors duration-150 hover:border-line-hover"
          >
            Continue with {p.label}
          </a>
        ))}

        {providers.length > 0 && (
          <div className="my-6 flex items-center gap-4">
            <span className="h-px flex-1 bg-line" />
            <span className="text-[11px] uppercase tracking-[0.1em] text-ink-faint">or</span>
            <span className="h-px flex-1 bg-line" />
          </div>
        )}

        <form onSubmit={submit} className="space-y-3">
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" autoComplete="email" className={inputCls} />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" autoComplete="current-password" className={inputCls} />
          {error && <p className="text-sm text-ink-soft">{error}</p>}
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-pill bg-white py-3 text-sm font-medium text-bg transition-colors duration-150 hover:bg-[#E8E8E8] disabled:opacity-50"
          >
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="mt-8 text-center text-[13px] text-ink-muted">
          New here?{' '}
          <Link to="/start" className="text-ink transition-colors duration-150 hover:underline">
            Start a project →
          </Link>
        </p>
      </main>
    </>
  )
}
