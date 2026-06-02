import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, AlertTriangle, RefreshCw, Shield, ShieldAlert, Users } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { fetchAuditTrail, fetchAuthMetrics, fetchQuotaMetrics, triggerUsageRollup } from '../utils/api'

const card = { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 16, padding: '20px 22px', boxShadow: 'var(--shadow-sm)' }

const EVENT_COLOR = (e) => (
  e === 'reuse_detected' || e === 'lockout' ? '#B91C1C'
    : e === 'login_failed' ? '#D97706'
    : e === 'login' || e === 'signup' ? '#059669'
    : 'var(--text-muted)'
)

export default function Admin() {
  const { user, loading } = useAuth()
  const nav = useNavigate()
  const [auth, setAuth] = useState(null)
  const [quota, setQuota] = useState(null)
  const [audit, setAudit] = useState([])
  const [rolling, setRolling] = useState(false)

  const load = () => {
    fetchAuthMetrics().then(setAuth).catch(() => {})
    fetchQuotaMetrics().then(setQuota).catch(() => {})
    fetchAuditTrail(60).then((d) => setAudit(d.events || [])).catch(() => {})
  }
  useEffect(() => {
    if (loading) return
    if (!user) { nav('/login', { state: { from: '/admin' } }); return }
    if (user.role === 'admin') load()
  }, [user, loading]) // eslint-disable-line

  if (loading || !user) return <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>Loading…</div>

  if (user.role !== 'admin') {
    return (
      <div style={{ maxWidth: 560, margin: '60px auto', padding: '0 18px', textAlign: 'center' }}>
        <ShieldAlert size={34} color="#B91C1C" />
        <h1 style={{ fontSize: 22, fontWeight: 800, fontFamily: 'DM Sans', marginTop: 12 }}>Admin access required</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14, marginTop: 6 }}>
          Your role is <strong>{user.role}</strong>. This console is restricted to admin accounts.
          Nothing is hidden behind a fake screen — the API itself returns 403.
        </p>
      </div>
    )
  }

  const runRollup = async () => { setRolling(true); try { await triggerUsageRollup() } finally { setRolling(false); load() } }

  const securityTiles = [
    ['Users', auth?.users_total, Users, 'var(--indigo)'],
    ['Active sessions', auth?.active_sessions, Shield, 'var(--teal)'],
    ['Active API keys', auth?.active_api_keys, Activity, '#0EA5E9'],
    ['Logins', auth?.logins, Shield, '#059669'],
    ['Login failures', auth?.login_failures, AlertTriangle, '#D97706'],
    ['Lockouts', auth?.lockouts, ShieldAlert, '#B91C1C'],
    ['Token reuse detected', auth?.reuse_detected, ShieldAlert, '#B91C1C'],
    ['Quota exceeded', auth?.quota_exceeded, AlertTriangle, '#D97706'],
  ]

  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '28px 18px 64px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)' }}>Admin console</h1>
          <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>Security, quota health & audit trail.</p>
        </div>
        <button onClick={runRollup} disabled={rolling} style={{ display: 'inline-flex', alignItems: 'center', gap: 7, padding: '9px 15px', borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: 13.5, cursor: 'pointer', opacity: rolling ? 0.6 : 1 }}>
          <RefreshCw size={15} /> {rolling ? 'Rolling…' : 'Run usage rollup'}
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 9, fontSize: 12.5, color: 'var(--text-muted)', background: 'var(--bg-card2)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '10px 14px' }}>
        Shared state: <strong style={{ color: 'var(--text-secondary)' }}>{quota?.shared_state_backend || '—'}</strong>
        · {quota?.note || 'Rate counters are in-process and reset on restart.'}
      </div>

      {/* Security tiles */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12 }}>
        {securityTiles.map(([label, value, Icon, color]) => (
          <div key={label} style={{ ...card, padding: '15px 17px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 7 }}>
              <Icon size={14} color={color} /><span className="stat-label">{label}</span>
            </div>
            <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'DM Sans' }}>{value ?? '—'}</div>
          </div>
        ))}
      </div>

      {/* Quota / top consumers */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <Activity size={16} color="var(--teal)" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>API consumption</span>
          <span style={{ marginLeft: 'auto', fontSize: 12.5, color: 'var(--text-muted)' }}>
            exhaustion {((quota?.exhaustion_rate ?? 0) * 100).toFixed(1)}% · throttle {((quota?.throttle_rate ?? 0) * 100).toFixed(1)}%
          </span>
        </div>
        {(quota?.top_consumers || []).length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No metered API usage recorded yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
            {quota.top_consumers.map((k) => (
              <div key={k.prefix} style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '8px 13px' }}>
                <code style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{k.prefix}…</code>
                <span style={{ fontSize: 12.5, color: 'var(--text-muted)' }}>{k.name}</span>
                <span style={{ fontSize: 12, color: 'var(--text-disabled)' }}>{k.email}</span>
                <span style={{ marginLeft: 'auto', fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>{k.requests}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Audit trail */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Shield size={16} color="var(--indigo)" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Audit trail</span>
          <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-disabled)' }}>append-only · compliance evidence</span>
        </div>
        {audit.length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No audit events yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5, maxHeight: 360, overflowY: 'auto' }}>
            {audit.map((e) => (
              <div key={e.id} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12.5, padding: '6px 4px', borderBottom: '1px solid var(--border-faint)' }}>
                <span style={{ fontWeight: 700, color: EVENT_COLOR(e.event), minWidth: 130 }}>{e.event}</span>
                <span style={{ color: 'var(--text-muted)' }}>{e.user_id ? `user ${e.user_id}` : '—'}</span>
                <span style={{ color: 'var(--text-disabled)' }}>{e.actor_ip || ''}</span>
                <span style={{ marginLeft: 'auto', color: 'var(--text-disabled)' }}>{e.at ? new Date(e.at).toLocaleString() : ''}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
