import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check, Copy, KeyRound, Plus, RefreshCw, Trash2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { createApiKey, listApiKeys, regenApiKey, revokeApiKey } from '../utils/api'

const card = { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 16, padding: '20px 22px', boxShadow: 'var(--shadow-sm)' }
const iconBtn = { display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 30, height: 30, borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg-card)', cursor: 'pointer', color: 'var(--text-muted)' }

export default function ApiKeys() {
  const { user, loading } = useAuth()
  const nav = useNavigate()
  const [keys, setKeys] = useState([])
  const [name, setName] = useState('')
  const [newKey, setNewKey] = useState(null)
  const [busy, setBusy] = useState(false)
  const [copied, setCopied] = useState(false)

  const load = () => listApiKeys().then(setKeys).catch(() => {})
  useEffect(() => {
    if (loading) return
    if (!user) { nav('/login', { state: { from: '/api-keys' } }); return }
    load()
  }, [user, loading]) // eslint-disable-line

  if (loading || !user) return <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>Loading…</div>

  const create = async () => {
    setBusy(true)
    try { setNewKey(await createApiKey(name || 'default')); setName(''); load() } finally { setBusy(false) }
  }
  const regen = async (id) => { setNewKey(await regenApiKey(id)); load() }
  const revoke = async (id) => { await revokeApiKey(id).catch(() => {}); load() }
  const copy = (txt) => { try { navigator.clipboard.writeText(txt); setCopied(true); setTimeout(() => setCopied(false), 1500) } catch { /* ignore */ } }

  return (
    <div style={{ maxWidth: 880, margin: '0 auto', padding: '28px 18px 64px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div>
        <h1 style={{ fontSize: 26, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)' }}>API keys</h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
          Authenticate the metered Developer API with the <code>X-API-Key</code> header. Quota + rate limits apply per your plan.
        </p>
      </div>

      <div style={card}>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Key name (e.g. production)" style={{ flex: 1, minWidth: 180, padding: '10px 13px', borderRadius: 10, border: '1px solid var(--border)', fontSize: 14, fontFamily: 'inherit', background: 'var(--bg-card)', outline: 'none' }} />
          <button onClick={create} disabled={busy} style={{ display: 'inline-flex', alignItems: 'center', gap: 7, padding: '10px 16px', borderRadius: 10, border: 'none', background: 'linear-gradient(135deg,#4338CA,#0D9488)', color: '#fff', fontWeight: 700, fontSize: 14, cursor: 'pointer', opacity: busy ? 0.7 : 1 }}>
            <Plus size={15} /> Create key
          </button>
        </div>
        {newKey && (
          <div style={{ marginTop: 14, background: 'rgba(5,150,105,0.06)', border: '1px solid rgba(5,150,105,0.25)', borderRadius: 11, padding: '13px 15px' }}>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: '#059669', marginBottom: 7 }}>New key — copy it now, it won't be shown again</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <code style={{ flex: 1, minWidth: 200, fontSize: 12.5, wordBreak: 'break-all', background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 8, padding: '8px 11px', color: 'var(--text-primary)' }}>{newKey.api_key}</code>
              <button onClick={() => copy(newKey.api_key)} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '8px 12px', borderRadius: 9, border: '1px solid var(--border)', background: 'var(--bg-card)', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}>
                {copied ? <><Check size={14} color="#059669" /> Copied</> : <><Copy size={14} /> Copy</>}
              </button>
            </div>
          </div>
        )}
      </div>

      <div style={card}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <KeyRound size={16} color="var(--indigo)" />
          <span style={{ fontWeight: 700, fontSize: 15, fontFamily: 'DM Sans' }}>Your keys</span>
        </div>
        {keys.length === 0 ? (
          <div style={{ fontSize: 13.5, color: 'var(--text-muted)' }}>No API keys yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
            {keys.map((k) => (
              <div key={k.id} style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '10px 13px', opacity: k.revoked ? 0.55 : 1 }}>
                <code style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)' }}>{k.prefix}…</code>
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{k.name}</span>
                {k.revoked && <span style={{ fontSize: 10.5, fontWeight: 700, color: '#B91C1C', background: 'rgba(239,68,68,0.08)', borderRadius: 100, padding: '1px 8px' }}>REVOKED</span>}
                <span style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
                  {!k.revoked && (
                    <>
                      <button onClick={() => regen(k.id)} title="Regenerate" style={iconBtn}><RefreshCw size={14} /></button>
                      <button onClick={() => revoke(k.id)} title="Revoke" style={{ ...iconBtn, color: '#B91C1C' }}><Trash2 size={14} /></button>
                    </>
                  )}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ ...card, background: 'var(--bg-card2)' }}>
        <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 8 }}>Example request</div>
        <code style={{ display: 'block', fontSize: 12, color: 'var(--text-secondary)', wordBreak: 'break-all', lineHeight: 1.6 }}>
          curl -H &quot;X-API-Key: lk_live_…&quot; {typeof location !== 'undefined' ? location.origin : ''}/api/v1/city/pune
        </code>
      </div>
    </div>
  )
}
