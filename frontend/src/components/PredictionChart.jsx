import {
  ComposedChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'

const CURRENT_YEAR = 2021

function buildChartData(history, prediction) {
  const data      = []
  const histYears = history.years
  const histAreas = history.urban_area_sqkm
  const predYears = prediction.timeline.years
  const predAreas = prediction.timeline.urban_area_sqkm
  const predPrices= prediction.timeline.land_price_inr_per_sqft
  const priceHist = prediction.city?.land_price_inr_per_sqft || {}

  const areaMap = {}
  histYears.forEach((y, i) => { areaMap[y] = histAreas[i] })

  const allYears = new Set([...histYears, ...predYears])
  allYears.forEach(year => {
    const entry = { year }
    if (areaMap[year] !== undefined)           entry.hist_area  = areaMap[year]
    const pi = predYears.indexOf(year)
    if (pi >= 0) { entry.pred_area = predAreas[pi]; entry.pred_price = predPrices[pi] }
    if (priceHist[String(year)] !== undefined) entry.hist_price = priceHist[String(year)]
    data.push(entry)
  })
  return data.sort((a, b) => a.year - b.year)
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: '#fff',
      border: '1.5px solid rgba(17, 24, 39, 0.1)',
      borderRadius: 12, padding: '12px 16px',
      fontSize: 13,
      boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
    }}>
      <div style={{ fontWeight: 700, color: '#111827', marginBottom: 8, fontSize: 13.5 }}>{label}</div>
      {payload.map(p => (
        <div key={p.dataKey} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, flexShrink: 0 }} />
          <span style={{ color: '#6B7280', fontWeight: 500 }}>{p.name}:</span>
          <span style={{ color: '#111827', fontWeight: 700 }}>
            {p.dataKey.includes('area') ? `${p.value?.toFixed(1)} km²` : `₹${p.value?.toLocaleString()}/sqft`}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function PredictionChart({ history, prediction }) {
  if (!history || !prediction) return (
    <div style={{ height: 280, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#9CA3AF', fontSize: 14 }}>
      No prediction data available
    </div>
  )

  const data = buildChartData(history, prediction)

  const axisStyle   = { fill: '#9CA3AF', fontSize: 11.5, fontWeight: 500 }
  const gridStyle   = { stroke: '#F3F4F6', strokeDasharray: '3 3' }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>

      {/* Urban Area Chart */}
      <div>
        <div className="section-title">
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#4338CA', flexShrink: 0 }} />
          Urban Area Growth — Historical + AI Forecast (km²)
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <ComposedChart data={data} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="areaHistGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#4338CA" stopOpacity={0.18} />
                <stop offset="95%" stopColor="#4338CA" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="areaPredGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#0D9488" stopOpacity={0.18} />
                <stop offset="95%" stopColor="#0D9488" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid {...gridStyle} vertical={false} />
            <XAxis dataKey="year" tick={axisStyle} axisLine={false} tickLine={false} />
            <YAxis tick={axisStyle} axisLine={false} tickLine={false} tickFormatter={v => `${v}km²`} width={54} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine x={CURRENT_YEAR} stroke="#F97316" strokeDasharray="4 4"
              label={{ value: 'Today', fill: '#F97316', fontSize: 10, fontWeight: 600 }} />
            <Area dataKey="hist_area" name="Actual Area"    fill="url(#areaHistGrad)" stroke="#4338CA" strokeWidth={2.5} dot={false} connectNulls />
            <Area dataKey="pred_area" name="Predicted Area" fill="url(#areaPredGrad)" stroke="#0D9488" strokeWidth={2.5} strokeDasharray="6 3" dot={false} connectNulls />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Land Price Chart */}
      <div>
        <div className="section-title">
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#D97706', flexShrink: 0 }} />
          Land Price Forecast — per sq ft
        </div>
        <ResponsiveContainer width="100%" height={210}>
          <ComposedChart data={data} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="priceHistGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#D97706" stopOpacity={0.18} />
                <stop offset="95%" stopColor="#D97706" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="pricePredGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#F97316" stopOpacity={0.18} />
                <stop offset="95%" stopColor="#F97316" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid {...gridStyle} vertical={false} />
            <XAxis dataKey="year" tick={axisStyle} axisLine={false} tickLine={false} />
            <YAxis tick={axisStyle} axisLine={false} tickLine={false}
              tickFormatter={v => v >= 1000 ? `₹${(v/1000).toFixed(0)}K` : `₹${v}`} width={54} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine x={CURRENT_YEAR} stroke="#F97316" strokeDasharray="4 4" />
            <Area dataKey="hist_price" name="Actual Price"    fill="url(#priceHistGrad)" stroke="#D97706" strokeWidth={2.5} dot={false} connectNulls />
            <Area dataKey="pred_price" name="Predicted Price" fill="url(#pricePredGrad)" stroke="#F97316" strokeWidth={2.5} strokeDasharray="6 3" dot={false} connectNulls />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Milestone summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        {[
          { label: 'Area 2026',      value: `${prediction.milestones?.area_2026_sqkm?.toFixed(1)} km²`, color: '#4338CA' },
          { label: 'Area 2031',      value: `${prediction.milestones?.area_2031_sqkm?.toFixed(1)} km²`, color: '#0D9488' },
          { label: 'Price Rise 5yr',  value: `+${prediction.milestones?.price_appreciation_5yr_pct}%`,  color: '#059669' },
          { label: 'Price Rise 10yr', value: `+${prediction.milestones?.price_appreciation_10yr_pct}%`, color: '#D97706' },
        ].map(item => (
          <div key={item.label} style={{
            background: 'var(--bg-base)',
            border: '1px solid var(--border-faint)',
            borderRadius: 12, padding: '13px 14px',
            boxShadow: 'var(--shadow-sm)',
          }}>
            <div className="stat-label" style={{ marginBottom: 5 }}>{item.label}</div>
            <div style={{ fontSize: 19, fontWeight: 800, color: item.color, letterSpacing: '-0.3px', fontFamily: 'DM Sans, sans-serif' }}>{item.value}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
