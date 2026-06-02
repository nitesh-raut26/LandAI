import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Cpu, KeyRound, LayoutDashboard, LogOut, Monitor, ShieldCheck, Star, Trash2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { fetchUsage, listSavedCities, listSessions, revokeSession, unsaveCityApi } from '../utils/api'

const card = { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 16, padding: '20px 22px', boxShadow: 'var(--shadow-sm)' }

export default function Account() {
  const { user, loading, logout, logoutAll } = useAuth()
  const nav = useNavigate()
  const [usage, setUsage] = useState(null)
  const [saved, setSaved] = useState([])
  const [sessions, setSessions] = useState([])

  const loadSessions = () => listSessions().then(setSessions).catch(() => {})
  useEffect(() => {
    if (loading) return
    if (!user) { nav('/login', { state: { from: '/account' } }); return }
    fetchUsage().then(setUsage).catch(() => {})
    listSavedCities().then(setSaved).catch(() => {})
    loadSessions()
  }, [user, loading]) // eslint-disable-line

  if (loading || !user) return <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>Loading…</div>

  const used = usage?.quota_used ?? 0
  const limit = usage?.daily_quota ?? 1000
  const pct = Math.min(100, Math.round((used / Math.max(limit, 1)) * 100))
  const remove = async (cid) => { await unsaveCityApi(cid).catch(() => {}); setSaved((s) => s.filter((x) => x.city_id !== cid)) }
  const revokeOne = async (id) => { await revokeSession(id).catch(() => {}); loadSessions() }
  const signOutEverywhere = async () => { await logoutAll(); nav('/') }

  return (
    <div style={{ maxWidth: 880, margin: '0 auto', padding: '28px 18px 64px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)' }}>Account</h1>
        <button onClick={async () => { await logout(); nav('/') }} style={{ display: 'inline-flex', alignItems: 'center', gap: 7, padding: '8px 14px', borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: 13.5, cursor: 'pointer' }}>
          <LogOut size={15} /> Log out
        </button>
      </div>

      <div style={card}>
        <div style={{ display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ width: 52, height: 52, borderRadius: 14, background: 'linear-gradient(135deg,#4338CA,#0D9488)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 800, fontSize: 22, fontFamily: 'DM Sans' }}>
            {user.email[0].toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 160 }}>
            <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', wordBreak: 'break-all' }}>{user.email}</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', display: 'flex', gap: 8, alignItems: 'center', marginTop: 4, flexWrap: 'wrap' }}>
              <span style={{ textTransform: 'capitalize' }}>Role: {user.role}</span>
              <span style={{ background: 'rgba(67,56,202,0.08)', color: 'var(--indigo)', border: '1px solid rgba(67,56,202,0.18)', padding: '1px 9px', borderRadius: 100, fontWeight: 700, textTransform: 'capitalize' }}>{usage?.tier_name || user.subscription_tier}</span>
            </div>
          </div>
        </div>
      </div>

      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <ShieldCheck size={16} color="var(--teal)" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Plan &amp; usage</span>
          <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-disabled)' }}>billing not live — no charges</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 12, marginBottom: 14 }}>
          {[
            ['Daily quota', limit.toLocaleString()],
            ['Used today', used.toLocaleString()],
            ['Remaining', (usage?.quota_remaining ?? limit).toLocaleString()],
            ['Rate limit', `${usage?.rate_per_minute ?? '—'}/min`],
          ].map(([l, v]) => (
            <div key={l} style={{ background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 13px' }}>
              <div className="stat-label">{l}</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'DM Sans' }}>{v}</div>
            </div>
          ))}
        </div>
        <div style={{ height: 8, borderRadius: 100, background: 'var(--bg-subtle)', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: pct > 85 ? '#EF4444' : 'linear-gradient(90deg,#4338CA,#0D9488)', borderRadius: 100 }} />
        </div>
        <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {(usage?.features || []).map((f) => (
            <span key={f} style={{ fontSize: 11.5, color: 'var(--text-muted)', background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 100, padding: '2px 9px' }}>{f.replace(/_/g, ' ')}</span>
          ))}
        </div>
      </div>

      <Link to="/dashboard" style={{ ...card, display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
        <LayoutDashboard size={18} color="var(--teal)" />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)' }}>Dashboard</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Watchlist, comparisons, saved searches &amp; API usage.</div>
        </div>
        <span style={{ color: 'var(--teal)', fontWeight: 700 }}>Open →</span>
      </Link>

      <Link to="/keys" style={{ ...card, display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
        <KeyRound size={18} color="var(--indigo)" />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)' }}>API keys</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Create keys for the metered Developer API (/api/v1).</div>
        </div>
        <span style={{ color: 'var(--indigo)', fontWeight: 700 }}>Manage →</span>
      </Link>

      <Link to="/model" style={{ ...card, display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
        <Cpu size={18} color="var(--teal)" />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)' }}>Model card &amp; leakage audit</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Forecast metrics, feature lineage, drift &amp; honest validation.</div>
        </div>
        <span style={{ color: 'var(--teal)', fontWeight: 700 }}>View →</span>
      </Link>

      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Star size={16} color="#D97706" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Saved cities</span>
          <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-disabled)' }}>persisted server-side</span>
        </div>
        {saved.length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No saved cities yet. Open a city and save it to sync across devices.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {saved.map((s) => (
              <div key={s.city_id} style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '9px 13px' }}>
                <Link to={`/city/${s.city_id}`} style={{ flex: 1, fontWeight: 600, color: 'var(--text-primary)', textTransform: 'capitalize' }}>{s.city_id}</Link>
                {s.note && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{s.note}</span>}
                <button onClick={() => remove(s.city_id)} title="Remove" style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-disabled)' }}><Trash2 size={15} /></button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Monitor size={16} color="var(--indigo)" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Active sessions</span>
          <button onClick={signOutEverywhere} style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 12px', borderRadius: 9, border: '1px solid var(--border)', background: 'var(--bg-card)', color: '#B91C1C', fontWeight: 600, fontSize: 12.5, cursor: 'pointer' }}>
            <LogOut size={13} /> Sign out everywhere
          </button>
        </div>
        {sessions.length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No active sessions.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {sessions.map((s) => (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '9px 13px' }}>
                <Monitor size={15} color="var(--text-muted)" />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: 13.5, color: 'var(--text-primary)' }}>{s.device_label || 'Unknown device'}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{s.ip || 'ip n/a'} · since {new Date(s.created_at).toLocaleDateString()}</div>
                </div>
                <button onClick={() => revokeOne(s.id)} title="Revoke this session" style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-disabled)' }}><Trash2 size={15} /></button>
              </div>
            ))}
          </div>
        )}
        <div style={{ marginTop: 10, fontSize: 11.5, color: 'var(--text-disabled)' }}>
          Refresh tokens rotate on use; reuse of a rotated token revokes the whole session family.
        </div>
      </div>
    </div>
  )
}
