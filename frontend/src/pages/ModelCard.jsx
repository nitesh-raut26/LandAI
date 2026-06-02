import { useEffect, useState } from 'react'
import { BadgeCheck, Boxes, CheckCircle2, ShieldCheck, XCircle } from 'lucide-react'
import { fetchDriftBaseline, fetchLeakageAudit, fetchModelCard, fetchModelRegistry, promoteModel } from '../utils/api'
import { useAuth } from '../context/AuthContext'

const card = { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 16, padding: '20px 22px', boxShadow: 'var(--shadow-sm)' }

export default function ModelCard() {
  const { user } = useAuth()
  const [info, setInfo] = useState(null)
  const [audit, setAudit] = useState(null)
  const [registry, setRegistry] = useState([])
  const [drift, setDrift] = useState(null)

  const loadRegistry = () => fetchModelRegistry().then((d) => setRegistry(d.models || [])).catch(() => {})
  useEffect(() => {
    fetchModelCard().then(setInfo).catch(() => {})
    fetchLeakageAudit().then(setAudit).catch(() => {})
    loadRegistry()
    fetchDriftBaseline().then(setDrift).catch(() => {})
  }, [])
  const promote = async (version) => { await promoteModel(version).catch(() => {}); loadRegistry() }

  if (!info) return <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>Loading model card…</div>

  const metrics = [
    ['Train R²', info.train_r2],
    ['CV R² (5-fold)', info.cv_r2_5fold],
    ['CV R² (repeated)', info.cv_r2_repeated_mean != null ? `${info.cv_r2_repeated_mean} ± ${info.cv_r2_repeated_std}` : '—'],
    ['RMSE', info.rmse],
    ['MAE', info.mae],
    ['Conformal coverage', info.conformal?.empirical_oof_coverage],
  ]
  const noLeak = audit && audit.leakage_detected === false

  return (
    <div style={{ maxWidth: 940, margin: '0 auto', padding: '28px 18px 64px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div>
        <h1 style={{ fontSize: 26, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)' }}>Model card</h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
          Land-price CAGR forecast — {info.backend} · <code>{info.model_version}</code> · {info.n_samples} samples · {info.n_features} features
        </p>
      </div>

      {/* Leakage banner — the honest headline */}
      <div style={{ ...card, borderColor: noLeak ? 'rgba(5,150,105,0.3)' : 'rgba(239,68,68,0.3)', background: noLeak ? 'rgba(5,150,105,0.05)' : 'rgba(239,68,68,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {noLeak ? <ShieldCheck size={20} color="#059669" /> : <XCircle size={20} color="#B91C1C" />}
          <span style={{ fontWeight: 800, fontSize: 16, fontFamily: 'DM Sans', color: noLeak ? '#059669' : '#B91C1C' }}>
            {noLeak ? 'No temporal leakage detected' : 'Leakage detected'}
          </span>
        </div>
        {audit && (
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 10, lineHeight: 1.55 }}>
            {audit.temporal_validation}
          </p>
        )}
        {audit?.honesty_note && (
          <p style={{ fontSize: 12.5, color: 'var(--text-muted)', marginTop: 8, fontStyle: 'italic' }}>{audit.honesty_note}</p>
        )}
      </div>

      {/* Metrics */}
      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <BadgeCheck size={16} color="var(--indigo)" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Validation metrics</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
          {metrics.map(([l, v]) => (
            <div key={l} style={{ background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 13px' }}>
              <div className="stat-label">{l}</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'DM Sans' }}>{v ?? '—'}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Feature audit: active vs excluded */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
        <div style={card}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 12 }}>
            <CheckCircle2 size={15} color="#059669" /> Active features ({(info.features || []).length})
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7 }}>
            {(info.features || []).map((f) => (
              <span key={f} style={{ fontSize: 12, fontWeight: 600, color: '#059669', background: 'rgba(5,150,105,0.08)', border: '1px solid rgba(5,150,105,0.2)', borderRadius: 100, padding: '3px 11px' }}>{f}</span>
            ))}
          </div>
        </div>
        <div style={card}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 12 }}>
            <XCircle size={15} color="#B91C1C" /> Excluded as leaky ({Object.keys(audit?.excluded_features || {}).length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
            {Object.entries(audit?.excluded_features || {}).map(([f, why]) => (
              <div key={f} style={{ fontSize: 12 }}>
                <code style={{ color: '#B91C1C', fontWeight: 700 }}>{f}</code>
                <span style={{ color: 'var(--text-muted)' }}> — {why}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Feature importances */}
      {(info.feature_importances || []).length > 0 && (
        <div style={card}>
          <div style={{ fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 12 }}>Feature importances</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {info.feature_importances.slice(0, 8).map((fi) => {
              const max = info.feature_importances[0].importance || 1
              return (
                <div key={fi.feature} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)', minWidth: 170 }}>{fi.feature}</span>
                  <div style={{ flex: 1, height: 8, background: 'var(--bg-subtle)', borderRadius: 100, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${Math.round((fi.importance / max) * 100)}%`, background: 'linear-gradient(90deg,#4338CA,#0D9488)', borderRadius: 100 }} />
                  </div>
                  <span style={{ fontSize: 11.5, color: 'var(--text-muted)', minWidth: 44, textAlign: 'right' }}>{fi.importance}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Registry + drift */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
        <div style={card}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 12 }}>
            <Boxes size={15} color="var(--indigo)" /> Model registry
          </div>
          {registry.length === 0 ? <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>No registered models.</div> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
              {registry.map((m) => (
                <div key={m.version} style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '8px 12px' }}>
                  <code style={{ fontSize: 11.5, color: 'var(--text-primary)', fontWeight: 600 }}>{m.version}</code>
                  <span style={{ fontSize: 11, fontWeight: 700, color: m.status === 'production' ? '#059669' : 'var(--text-muted)', background: m.status === 'production' ? 'rgba(5,150,105,0.08)' : 'var(--bg-subtle)', borderRadius: 100, padding: '1px 8px' }}>{m.status}</span>
                  <span style={{ marginLeft: 'auto', fontSize: 11.5, color: 'var(--text-muted)' }}>cv R² {m.metrics?.cv_r2_5fold ?? '—'}</span>
                  {user?.role === 'admin' && m.status !== 'production' && (
                    <button onClick={() => promote(m.version)} title="Promote to production (rollback to this version)" style={{ fontSize: 11, fontWeight: 600, color: 'var(--indigo)', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '3px 9px', cursor: 'pointer' }}>Set production</button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        <div style={card}>
          <div style={{ fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans', marginBottom: 10 }}>Drift monitoring</div>
          <div style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Method: <strong style={{ color: 'var(--text-secondary)' }}>{drift?.method || 'PSI'}</strong>. Status:{' '}
            <strong style={{ color: 'var(--text-secondary)' }}>{drift?.status || '—'}</strong>.
            <div style={{ marginTop: 6 }}>{drift?.note}</div>
          </div>
        </div>
      </div>
    </div>
  )
}
