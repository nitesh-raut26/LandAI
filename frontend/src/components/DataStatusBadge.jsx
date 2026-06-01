import { useDataTrust } from '../context/DataTrustContext'
import { KIND, timeAgo } from '../utils/trust'

/**
 * Honest per-panel data-source badge.
 * `kind`: real_live | real | model | curated | heuristic | simulated
 * When the backend is unreachable, ANYTHING on screen is the curated offline
 * mirror — so the badge overrides to "Offline snapshot" regardless of `kind`.
 */
export default function DataStatusBadge({ kind = 'curated', source, updatedAt, compact = false }) {
  const trust = useDataTrust()
  const offline = trust.backendOnline === false
  const k = offline ? KIND.offline : (KIND[kind] || KIND.curated)

  const parts = []
  if (source && !offline) parts.push(source)
  if (updatedAt && !offline) {
    const ta = timeAgo(updatedAt)
    if (ta) parts.push(ta)
  }

  return (
    <span title={k.tip} style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      fontSize: compact ? 11 : 12, fontWeight: 600, color: 'var(--text-secondary)',
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 100, padding: compact ? '2px 9px' : '4px 11px',
      boxShadow: 'var(--shadow-sm)', whiteSpace: 'nowrap', cursor: 'help',
    }}>
      <span style={{
        width: 7, height: 7, borderRadius: '50%', background: k.dot, flexShrink: 0,
        boxShadow: (kind === 'real_live' && !offline) ? `0 0 0 3px ${k.dot}22` : 'none',
      }} />
      <span>{k.label}</span>
      {parts.length > 0 && (
        <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>· {parts.join(' · ')}</span>
      )}
    </span>
  )
}
