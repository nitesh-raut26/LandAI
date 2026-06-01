// Shared helpers for the Data Trust Layer — keep the honest vocabulary in one place.

// data_class -> visual identity. Mirrors backend /api/system/provenance.
export const KIND = {
  real_live: { dot: '#059669', label: 'Live',            tip: 'Live from an external source, with provenance' },
  real:      { dot: '#0D9488', label: 'Computed',        tip: 'Computed with real algorithms on real geometry' },
  model:     { dot: '#4338CA', label: 'Model',           tip: 'Trained ML model output (see model card)' },
  curated:   { dot: '#F59E0B', label: 'Curated',         tip: 'Curated/expert dataset — not live market data' },
  heuristic: { dot: '#8B5CF6', label: 'Heuristic',       tip: 'Rule/formula-based estimate' },
  simulated: { dot: '#3B82F6', label: 'Simulated',       tip: 'Procedural model input (not real-world sensed)' },
  offline:   { dot: '#EF4444', label: 'Offline snapshot', tip: 'Backend unreachable — showing last-known curated data' },
  checking:  { dot: '#9CA3AF', label: 'Checking…',       tip: 'Checking backend status' },
}

export function timeAgo(iso) {
  if (!iso) return null
  const t = typeof iso === 'string' ? Date.parse(iso) : Number(iso)
  if (Number.isNaN(t)) return null
  const s = Math.max(0, (Date.now() - t) / 1000)
  if (s < 60) return `${Math.round(s)}s ago`
  if (s < 3600) return `${Math.round(s / 60)}m ago`
  if (s < 86400) return `${Math.round(s / 3600)}h ago`
  return `${Math.round(s / 86400)}d ago`
}

// freshness score 0..1 -> tone
export function freshnessTone(score) {
  if (score == null) return { color: '#9CA3AF', label: '—' }
  if (score >= 0.66) return { color: '#059669', label: 'Fresh' }
  if (score >= 0.33) return { color: '#F59E0B', label: 'Aging' }
  return { color: '#EF4444', label: 'Stale' }
}

// accepts 0..1 or 0..100
export function confidenceTone(v) {
  const x = v == null ? null : (v > 1 ? v / 100 : v)
  if (x == null) return { color: '#9CA3AF', pct: 0, label: '—' }
  if (x >= 0.75) return { color: '#059669', pct: x * 100, label: 'High' }
  if (x >= 0.5)  return { color: '#0D9488', pct: x * 100, label: 'Moderate' }
  if (x >= 0.3)  return { color: '#F59E0B', pct: x * 100, label: 'Low' }
  return { color: '#EF4444', pct: x * 100, label: 'Very low' }
}
