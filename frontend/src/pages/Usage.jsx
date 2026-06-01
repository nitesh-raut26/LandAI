import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Activity, KeyRound, Info } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { fetchUsageHistory } from '../utils/api'

const card = { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 16, padding: '20px 22px', boxShadow: 'var(--shadow-sm)' }
const RANGES = [7, 30, 90]

export default function Usage() {
  const { user, loading } = useAuth()
  const nav = useNavigate()
  const [days, setDays] = useState(30)
  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(true)

  useEffect(() => {
    if (loading) return
    if (!user) { nav('/login', { state: { from: '/usage' } }); return }
    setBusy(true)
    fetchUsageHistory(days).then(setData).catch(() => {}).finally(() => setBusy(false))
  }, [user, loading, days]) // eslint-disable-line

  if (loading || !user) return <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>Loading…</div>

  const series = data?.series || []
  const peak = Math.max(1, ...series.map((p) => p.count))
  const total = data?.total_requests ?? 0

  return (
    <div style={{ maxWidth: 980, margin: '0 auto', padding: '28px 18px 64px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)' }}>API usage</h1>
          <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>Metered Developer API requests from your keys.</p>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {RANGES.map((d) => (
            <button key={d} onClick={() => setDays(d)} style={{ padding: '7px 13px', borderRadius: 9, border: `1px solid ${days === d ? 'var(--indigo)' : 'var(--border)'}`, background: days === d ? 'rgba(67,56,202,0.08)' : 'var(--bg-card)', color: days === d ? 'var(--indigo)' : 'var(--text-muted)', fontWeight: 700, fontSize: 13, cursor: 'pointer' }}>{d}d</button>
          ))}
        </div>
      </div>

      {/* Honest provenance note */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 9, fontSize: 12.5, color: 'var(--text-muted)', background: 'var(--bg-card2)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 14px' }}>
        <Info size={15} style={{ flexShrink: 0, marginTop: 1 }} />
        <span>{data?.note || 'Web-app calls are not metered — only requests authenticated with an API key against /api/v1 appear here.'}</span>
      </div>

      {/* Day series */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <Activity size={16} color="var(--teal)" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Requests · last {days} days</span>
          <span style={{ marginLeft: 'auto', fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>{total.toLocaleString()} total</span>
        </div>
        {busy ? (
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Loading…</div>
        ) : total === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)', padding: '8px 0' }}>
            No metered calls yet. <Link to="/keys" style={{ color: 'var(--indigo)', fontWeight: 600 }}>Create an API key</Link> and call <code>/api/v1/city/&#123;id&#125;</code> with the <code>X-API-Key</code> header.
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 120 }}>
            {series.map((p) => (
              <div key={p.date} title={`${p.date}: ${p.count}`} style={{ flex: 1, minWidth: 2, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', height: '100%' }}>
                <div style={{ height: `${(p.count / peak) * 100}%`, minHeight: p.count ? 3 : 0, background: 'linear-gradient(180deg,#4338CA,#0D9488)', borderRadius: '3px 3px 0 0' }} />
              </div>
            ))}
          </div>
        )}
      </div>

      {total > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
          {/* Top endpoints */}
          <div style={card}>
            <div style={{ fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 12 }}>Top endpoints</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
              {(data.by_endpoint || []).map((e) => (
                <div key={e.path} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <code style={{ flex: 1, fontSize: 12, color: 'var(--text-secondary)', wordBreak: 'break-all' }}>{e.path}</code>
                  <span style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>{e.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Per-key */}
          <div style={card}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 12 }}>
              <KeyRound size={15} color="var(--indigo)" /> By key
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
              {(data.by_key || []).map((k) => (
                <div key={k.prefix} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <code style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{k.prefix}…</code>
                  <span style={{ fontSize: 12.5, color: 'var(--text-muted)' }}>{k.name}</span>
                  <span style={{ marginLeft: 'auto', fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>{k.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Status mix */}
          <div style={card}>
            <div style={{ fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 12 }}>Response status</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {Object.entries(data.by_status || {}).map(([s, n]) => (
                <span key={s} style={{ fontSize: 12.5, fontWeight: 700, padding: '4px 11px', borderRadius: 100, background: s.startsWith('2') ? 'rgba(5,150,105,0.08)' : 'rgba(239,68,68,0.08)', color: s.startsWith('2') ? '#059669' : '#B91C1C', border: `1px solid ${s.startsWith('2') ? 'rgba(5,150,105,0.2)' : 'rgba(239,68,68,0.2)'}` }}>{s} · {n}</span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
