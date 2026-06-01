import DataStatusBadge from './DataStatusBadge'
import FreshnessIndicator from './FreshnessIndicator'
import ConfidenceMeter from './ConfidenceMeter'

/**
 * Horizontal provenance strip placed under a data panel. Pass a `provenance`
 * envelope (from /api/live/*): { source, license, fetched_at, confidence,
 * freshness_score, cache_hit, legality_note }. `kind` controls the badge class.
 */
export default function ProvenanceStrip({ provenance, kind = 'real_live', note }) {
  const p = provenance || {}
  const tip = p.legality_note || note
  return (
    <div style={{
      display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '10px 16px',
      padding: '9px 14px', borderRadius: 12, background: 'var(--bg-card2)',
      border: '1px solid var(--border-faint)', fontSize: 12,
    }}>
      <DataStatusBadge kind={kind} source={p.source} updatedAt={p.fetched_at} compact />
      {p.freshness_score != null && <FreshnessIndicator score={p.freshness_score} updatedAt={p.fetched_at} />}
      {p.confidence != null && <ConfidenceMeter value={p.confidence} />}
      {p.license && <span style={{ color: 'var(--text-muted)' }}>· {p.license}</span>}
      {p.cache_hit != null && (
        <span style={{ color: 'var(--text-muted)' }}>· {p.cache_hit ? 'cached' : 'fresh fetch'}</span>
      )}
      {tip && (
        <span title={tip} style={{ color: 'var(--text-disabled)', cursor: 'help', marginLeft: 'auto' }}>
          ⓘ provenance
        </span>
      )}
    </div>
  )
}
