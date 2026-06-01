import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LogIn } from 'lucide-react'
import AuthShell, { inputStyle, labelStyle } from '../components/AuthShell'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const nav = useNavigate()
  const loc = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault(); setErr(null); setBusy(true)
    try {
      await login(email.trim(), password)
      nav(loc.state?.from || '/account')
    } catch (ex) {
      const d = ex?.response?.data?.detail
      setErr(typeof d === 'string' ? d : 'Login failed — check your credentials.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      title="Welcome back" subtitle="Sign in to your LandAI account"
      footer={<>No account? <Link to="/register" style={{ color: 'var(--indigo)', fontWeight: 600 }}>Create one</Link></>}
    >
      <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <label style={labelStyle}>Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} style={inputStyle} placeholder="you@example.com" autoComplete="email" />
        </label>
        <label style={labelStyle}>Password
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} style={inputStyle} placeholder="••••••••" autoComplete="current-password" />
        </label>
        {err && (
          <div style={{ fontSize: 13, color: '#B91C1C', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 9, padding: '8px 11px' }}>{err}</div>
        )}
        <button type="submit" disabled={busy} style={{
          background: 'linear-gradient(135deg,#4338CA,#0D9488)', color: '#fff', padding: '11px',
          borderRadius: 11, border: 'none', fontWeight: 700, fontSize: 14, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, opacity: busy ? 0.7 : 1,
        }}>
          {busy ? 'Signing in…' : <><LogIn size={16} /> Sign in</>}
        </button>
      </form>
    </AuthShell>
  )
}
