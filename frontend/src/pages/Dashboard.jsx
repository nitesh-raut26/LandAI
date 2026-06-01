import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity, ArrowRight, GitCompare, KeyRound, Search, Star, Trash2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { deleteSavedSearchApi, fetchDashboard, listSavedSearches } from '../utils/api'

const card = { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 16, padding: '20px 22px', boxShadow: 'var(--shadow-sm)' }
const chip = { display: 'inline-flex', alignItems: 'center', gap: 6, background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 100, padding: '5px 13px', fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', textTransform: 'capitalize', textDecoration: 'none' }

const queryToParams = (q = {}) => {
  const p = new URLSearchParams()
  if (q.state) p.set('state', q.state)
  if (q.tier != null && q.tier !== '') p.set('tier', q.tier)
  if (q.phase) p.set('phase', q.phase)
  return p.toString()
}

export default function Dashboard() {
  const { user, loading } = useAuth()
  const nav = useNavigate()
  const [data, setData] = useState(null)
  const [searches, setSearches] = useState([])

  const loadSearches = () => listSavedSearches().then(setSearches).catch(() => {})
  useEffect(() => {
    if (loading) return
    if (!user) { nav('/login', { state: { from: '/dashboard' } }); return }
    fetchDashboard().then(setData).catch(() => {})
    loadSearches()
  }, [user, loading]) // eslint-disable-line

  if (loading || !user) return <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>Loading…</div>

  const c = data?.counts || {}
  const stats = [
    ['Watchlist', c.watchlist ?? 0, Star, '#D97706'],
    ['Saved cities', c.saved_cities ?? 0, Star, '#4338CA'],
    ['Comparisons', c.compares ?? 0, GitCompare, '#0D9488'],
    ['Saved searches', c.saved_searches ?? 0, Search, '#7C3AED'],
    ['API keys', c.api_keys ?? 0, KeyRound, '#0EA5E9'],
  ]
  const runSearch = (q) => { const qs = queryToParams(q); nav(qs ? `/?${qs}` : '/') }
  const removeSearch = async (id) => { await deleteSavedSearchApi(id).catch(() => {}); setSearches((s) => s.filter((x) => x.id !== id)) }

  return (
    <div style={{ maxWidth: 980, margin: '0 auto', padding: '28px 18px 64px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)' }}>Dashboard</h1>
          <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>Your saved intelligence — synced server-side to <span style={{ wordBreak: 'break-all' }}>{user.email}</span>.</p>
        </div>
        <Link to="/usage" style={{ display: 'inline-flex', alignItems: 'center', gap: 7, padding: '9px 15px', borderRadius: 10, border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text-secondary)', fontWeight: 600, fontSize: 13.5, textDecoration: 'none' }}>
          <Activity size={15} /> API usage
        </Link>
      </div>

      {/* Stat tiles */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12 }}>
        {stats.map(([label, value, Icon, color]) => (
          <div key={label} style={{ ...card, padding: '16px 18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <Icon size={15} color={color} />
              <span className="stat-label">{label}</span>
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'DM Sans' }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Watchlist */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Star size={16} color="#D97706" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Watchlist</span>
          <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-disabled)' }}>synced across devices</span>
        </div>
        {(data?.watchlist || []).length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>Nothing watched yet. Tap <strong>Watch</strong> on any city to track it here.</div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {data.watchlist.map((id) => (
              <Link key={id} to={`/city/${id}`} style={chip}><Star size={12} fill="#D97706" color="#D97706" />{id}</Link>
            ))}
          </div>
        )}
      </div>

      {/* Recent comparisons */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <GitCompare size={16} color="#0D9488" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Recent comparisons</span>
        </div>
        {(data?.recent_compares || []).length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No comparisons yet. <Link to="/compare" style={{ color: 'var(--teal)', fontWeight: 600 }}>Compare two cities →</Link></div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.recent_compares.map((cm) => (
              <Link key={cm.id} to={`/compare?a=${cm.city_a}&b=${cm.city_b}`} style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '9px 13px', textDecoration: 'none' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)', textTransform: 'capitalize' }}>{cm.city_a}</span>
                <ArrowRight size={13} color="var(--text-disabled)" />
                <span style={{ fontWeight: 600, color: 'var(--text-primary)', textTransform: 'capitalize' }}>{cm.city_b}</span>
                <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-disabled)' }}>Open →</span>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Saved searches */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <Search size={16} color="#7C3AED" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Saved searches</span>
        </div>
        {searches.length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No saved searches. Apply filters on <Link to="/" style={{ color: 'var(--indigo)', fontWeight: 600 }}>Explore</Link> and save them for one-tap reuse.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {searches.map((s) => (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '9px 13px' }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{s.label}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    {Object.entries(s.query).map(([k, v]) => `${k}: ${v}`).join(' · ') || 'all cities'}
                  </div>
                </div>
                <button onClick={() => runSearch(s.query)} style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '6px 12px', borderRadius: 9, border: '1px solid var(--border)', background: 'var(--bg-card)', cursor: 'pointer', fontWeight: 600, fontSize: 12.5, color: 'var(--indigo)' }}>Run</button>
                <button onClick={() => removeSearch(s.id)} title="Delete" style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-disabled)' }}><Trash2 size={15} /></button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Link to="/account" style={{ ...card, flex: 1, minWidth: 200, display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
          <Star size={18} color="var(--indigo)" />
          <div style={{ flex: 1 }}><div style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)' }}>Account &amp; plan</div><div style={{ fontSize: 12.5, color: 'var(--text-muted)' }}>Quota, saved cities, profile</div></div>
        </Link>
        <Link to="/keys" style={{ ...card, flex: 1, minWidth: 200, display: 'flex', alignItems: 'center', gap: 12, textDecoration: 'none' }}>
          <KeyRound size={18} color="var(--indigo)" />
          <div style={{ flex: 1 }}><div style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)' }}>API keys</div><div style={{ fontSize: 12.5, color: 'var(--text-muted)' }}>Metered Developer API</div></div>
        </Link>
      </div>
    </div>
  )
}
