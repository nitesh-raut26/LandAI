import { useState, useEffect, useMemo } from 'react'
import {
  ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from 'recharts'
import { History, ArrowRight, Loader2 } from 'lucide-react'
import { fetchTimeMachine, formatPrice } from '../utils/api'
import ProvenanceStrip from './ProvenanceStrip'

/**
 * Time Machine (Vision §3.6): replays a more-developed twin city's REAL price
 * trajectory onto this city's projected future — "where will it be in N years?".
 * Data-driven (observed twin history + the forecast CAGR), not satellite imagery.
 */
export default function TimeMachine({ cityId }) {
  const [tm, setTm] = useState(undefined)  // undefined = loading, null = no twin

  useEffect(() => {
    if (!cityId) return
    setTm(undefined)
    fetchTimeMachine(cityId).then(setTm).catch(() => setTm(null))
  }, [cityId])

  const chartData = useMemo(() => {
    if (!tm) return []
    const byYear = {}
    tm.projection.forEach(p => { byYear[p.year] = { year: p.year, projected: p.projected_price_inr_per_sqft } })
    tm.twin_overlay.forEach(o => {
      const y = o.target_equivalent_year
      byYear[y] = { ...(byYear[y] || { year: y }), twinRef: o.twin_price_inr_per_sqft, twinYear: o.twin_year }
    })
    return Object.values(byYear).sort((a, b) => a.year - b.year)
  }, [tm])

  if (tm === undefined) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '40px 0', color: '#9CA3AF' }}>
      <Loader2 size={20} className="spin" style={{ animation: 'spin 0.9s linear infinite' }} /> Loading Time Machine…
    </div>
  )
  if (!tm) return (
    <div style={{ padding: '28px 8px', color: '#6B7280', fontSize: 14, lineHeight: 1.6 }}>
      No historical twin is available for this city, so the Time Machine has nothing to replay. Cities with a more-developed twin (see the Twin City tab) get a projected trajectory here.
    </div>
  )

  const TILES = [
    { label: 'Resembles twin from', value: `~${tm.lag_years} yrs ago`, color: '#4338CA' },
    { label: 'Twin is pricier by', value: `${tm.twin_price_multiple}×`, color: '#0D9488' },
    { label: 'Reaches twin price by', value: tm.parity_year, color: '#D97706' },
    { label: 'Projected CAGR', value: `${tm.projected_price_cagr_pct}%`, color: '#059669' },
  ]

  return (
    <div>
      <div className="section-title"><History size={13} /> Time Machine — {tm.city_name} → {tm.twin_city_name}</div>

      <div style={{
        display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap',
        background: 'linear-gradient(135deg, rgba(67,56,202,0.05), rgba(13,148,136,0.05))',
        border: '1px solid rgba(67,56,202,0.16)', borderRadius: 12, padding: '13px 16px', marginBottom: 16,
      }}>
        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{tm.city_name}</span>
        <ArrowRight size={14} color="#9CA3AF" />
        <span style={{ fontSize: 13.5, color: '#6B7280', lineHeight: 1.55 }}>{tm.headline}</span>
      </div>

      <div className="grid-4" style={{ gap: 12, marginBottom: 18 }}>
        {TILES.map(t => (
          <div key={t.label} style={{ background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 12, padding: '12px 14px' }}>
            <div style={{ fontSize: 10.5, color: '#9CA3AF', fontWeight: 500, marginBottom: 4 }}>{t.label}</div>
            <div style={{ fontSize: 19, fontWeight: 800, color: t.color, fontFamily: 'DM Sans, sans-serif' }}>{t.value}</div>
          </div>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData} margin={{ top: 8, right: 16, bottom: 4, left: 4 }}>
          <CartesianGrid stroke="#F3F4F6" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="year" tick={{ fill: '#9CA3AF', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#9CA3AF', fontSize: 11 }} axisLine={false} tickLine={false} width={48}
            tickFormatter={v => formatPrice(v)} />
          <Tooltip
            formatter={(val, name) => [formatPrice(val), name === 'projected' ? `${tm.city_name} projected` : `${tm.twin_city_name} actual`]}
            labelFormatter={y => `Year ${y}`}
            contentStyle={{ borderRadius: 10, border: '1.5px solid rgba(17,24,39,0.1)', fontSize: 12.5 }} />
          <ReferenceLine y={tm.twin_current_price_inr_per_sqft} stroke="#0D9488" strokeDasharray="5 4"
            label={{ value: `${tm.twin_city_name} today`, position: 'insideTopRight', fontSize: 10.5, fill: '#0D9488' }} />
          <Line type="monotone" dataKey="projected" stroke="#4338CA" strokeWidth={2.5} dot={false} name="projected" />
          <Scatter dataKey="twinRef" fill="#0D9488" name="twinRef" />
        </ComposedChart>
      </ResponsiveContainer>
      <div style={{ marginTop: 8 }}>
        <ProvenanceStrip kind="heuristic" provenance={{ source: 'Twin replay (observed history + forecast CAGR)' }}
          note={tm.method} />
      </div>
    </div>
  )
}
