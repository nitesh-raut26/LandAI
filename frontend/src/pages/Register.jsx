import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus } from 'lucide-react'
import AuthShell, { inputStyle, labelStyle } from '../components/AuthShell'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState(null)
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault(); setErr(null)
    if (password.length < 8) { setErr('Password must be at least 8 characters.'); return }
    setBusy(true)
    try {
      await register(email.trim(), password)
      nav('/account')
    } catch (ex) {
      const d = ex?.response?.data?.detail
      setErr(typeof d === 'string' ? d : 'Registration failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      title="Create your account" subtitle="Free Developer tier — 1,000 API requests/day"
      footer={<>Already have an account? <Link to="/login" style={{ color: 'var(--indigo)', fontWeight: 600 }}>Sign in</Link></>}
    >
      <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <label style={labelStyle}>Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} style={inputStyle} placeholder="you@example.com" autoComplete="email" />
        </label>
        <label style={labelStyle}>Password
          <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} style={inputStyle} placeholder="At least 8 characters" autoComplete="new-password" />
        </label>
        {err && (
          <div style={{ fontSize: 13, color: '#B91C1C', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 9, padding: '8px 11px' }}>{err}</div>
        )}
        <button type="submit" disabled={busy} style={{
          background: 'linear-gradient(135deg,#4338CA,#0D9488)', color: '#fff', padding: '11px',
          borderRadius: 11, border: 'none', fontWeight: 700, fontSize: 14, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, opacity: busy ? 0.7 : 1,
        }}>
          {busy ? 'Creating…' : <><UserPlus size={16} /> Create account</>}
        </button>
        <div style={{ fontSize: 11.5, color: 'var(--text-disabled)', textAlign: 'center', lineHeight: 1.5 }}>
          Passwords are hashed (never stored in plaintext). Billing is not live — no payment required.
        </div>
      </form>
    </AuthShell>
  )
}
