import { freshnessTone, timeAgo } from '../utils/trust'

/** Freshness meter for a provenanced dataset. `score` is 0..1. */
export default function FreshnessIndicator({ score, updatedAt }) {
  const tone = freshnessTone(score)
  const ta = timeAgo(updatedAt)
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-muted)' }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: tone.color, flexShrink: 0 }} />
      <span style={{ fontWeight: 600, color: tone.color }}>{tone.label}</span>
      {score != null && <span>({Math.round(score * 100)}%)</span>}
      {ta && <span>· {ta}</span>}
    </span>
  )
}
