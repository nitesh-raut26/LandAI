import { confidenceTone } from '../utils/trust'

/** Compact confidence meter. `value` accepts 0..1 or 0..100. */
export default function ConfidenceMeter({ value, label = 'Confidence', width = 88 }) {
  const tone = confidenceTone(value)
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, fontSize: 12, color: 'var(--text-muted)' }}>
      <span style={{ fontWeight: 500 }}>{label}</span>
      <span style={{
        width, height: 6, borderRadius: 100, background: 'var(--bg-subtle)',
        overflow: 'hidden', display: 'inline-block', flexShrink: 0,
      }}>
        <span style={{
          display: 'block', height: '100%',
          width: `${Math.max(4, Math.min(100, tone.pct))}%`,
          background: tone.color, borderRadius: 100,
        }} />
      </span>
      <span style={{ fontWeight: 600, color: tone.color }}>{tone.label}</span>
    </span>
  )
}
