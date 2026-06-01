import {
  ComposedChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { ArrowRight, Clock } from 'lucide-react'
import { tierColor, phaseColor } from '../utils/api'

export default function CityComparison({ targetCity, twin }) {
  if (!twin) return (
    <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-muted)' }}>
      No historical twin found for this city.
    </div>
  )

  const twinCity = twin.twin_city
  const lagYears = twin.lag_years
  const comp     = twin.comparison

  const chartData = []
  if (comp) {
    const targetYears = comp.city_a.history.area_years
    const targetAreas = comp.city_a.history.area_values
    const twinYears   = comp.city_b.history.area_years
    const twinAreas   = comp.city_b.history.area_values

    const allYears = [...new Set([...targetYears, ...twinYears.map(y => y - lagYears)])].sort()
    allYears.forEach(year => {
      const entry = { year }
      const ti  = targetYears.indexOf(year)
      if (ti >= 0) entry.target_area = targetAreas[ti]
      const twi = twinYears.indexOf(year + lagYears)
      if (twi >= 0) entry.twin_area = twinAreas[twi]
      chartData.push(entry)
    })
  }

  const CityCard = ({ city, label, color }) => {
    const tc = tierColor(city.tier)
    const pc = phaseColor(city.growth_phase)
    return (
      <div style={{
        background: 'var(--bg-base)',
        border: `1px solid ${color}20`,
        borderTop: `3px solid ${color}`,
        borderRadius: 14, padding: 18, flex: 1,
      }}>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.7px', marginBottom: 6, fontWeight: 600 }}>
          {label}
        </div>
        <div style={{ fontWeight: 800, fontSize: 18, color: 'var(--text-primary)', marginBottom: 3, fontFamily: 'DM Sans, sans-serif' }}>{city.name}</div>
        <div style={{ fontSize: 12.5, color: '#9CA3AF', marginBottom: 10, fontWeight: 500 }}>{city.state}</div>
        <div style={{ display: 'flex', gap: 5, marginBottom: 12, flexWrap: 'wrap' }}>
          <span style={{ background: `${tc}12`, color: tc, border: `1px solid ${tc}22`, padding: '2px 8px', borderRadius: 100, fontSize: 10.5, fontWeight: 600 }}>
            Tier {city.tier}
          </span>
          <span style={{ background: `${pc}12`, color: pc, border: `1px solid ${pc}22`, padding: '2px 8px', borderRadius: 100, fontSize: 10.5, fontWeight: 600, textTransform: 'capitalize' }}>
            {city.growth_phase}
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[
            { l: 'Pop 2021',   v: `${(city.population['2021'] / 1e6).toFixed(2)}M` },
            { l: 'Urban Area', v: `${city.urban_area_sqkm['2021']} km²` },
            { l: 'Land Price', v: `₹${city.land_price_inr_per_sqft['2021'].toLocaleString()}/sqft` },
            { l: 'Inv. Score', v: city.investment_score },
          ].map(({ l, v }) => (
            <div key={l}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 2, fontWeight: 500 }}>{l}</div>
              <div style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-primary)' }}>{v}</div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Twin match banner */}
      <div style={{
        background: 'rgba(67, 56, 202, 0.04)',
        border: '1px solid rgba(67, 56, 202, 0.16)',
        borderRadius: 14, padding: '16px 20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
          <Clock size={14} color="var(--indigo)" />
          <span style={{ color: 'var(--indigo)', fontWeight: 700, fontSize: 14.5, fontFamily: 'DM Sans, sans-serif' }}>Historical Twin Match</span>
          <span style={{
            background: 'rgba(67, 56, 202, 0.1)',
            color: 'var(--indigo)',
            border: '1px solid rgba(67, 56, 202, 0.22)',
            padding: '2px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600,
          }}>
            {twin.similarity_score}% similar
          </span>
        </div>
        <div style={{ fontSize: 14, color: '#6B7280', lineHeight: 1.65 }}>
          <strong style={{ color: '#111827' }}>{twinCity.name}</strong> was at a similar development stage
          approximately{' '}
          <strong style={{ color: 'var(--indigo)' }}>{lagYears} years ago</strong> — it is now a {twinCity.growth_phase} city at{' '}
          ₹{twinCity.land_price_inr_per_sqft['2021'].toLocaleString()}/sqft. If{' '}
          <strong style={{ color: '#111827' }}>{targetCity.name}</strong> follows the same trajectory,
          that's where it's headed.
        </div>
        {twin.match_reason && (
          <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 6 }}>
            Match reason: {twin.match_reason}
          </div>
        )}
      </div>

      {/* City cards */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'stretch', flexWrap: 'wrap' }}>
        <CityCard city={targetCity} label="Target City (Today)" color="#4338CA" />
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', gap: 5, flexShrink: 0, minWidth: 44,
        }}>
          <ArrowRight size={18} color="#9CA3AF" />
          <div style={{ fontSize: 10.5, color: '#9CA3AF', textAlign: 'center', fontWeight: 500 }}>{lagYears}yr lag</div>
        </div>
        <CityCard city={twinCity} label={`Twin City (+${lagYears} Yrs ahead)`} color="#0D9488" />
      </div>

      {/* Growth curve overlay */}
      {chartData.length > 0 && (
        <div>
          <div className="section-title">
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--indigo)', flexShrink: 0 }} />
            Growth Curve Overlay — Time-Shifted Comparison
          </div>
          <ResponsiveContainer width="100%" height={210}>
            <ComposedChart data={chartData} margin={{ top: 4, right: 14, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="targetGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#4338CA" stopOpacity={0.18} />
                  <stop offset="95%" stopColor="#4338CA" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="twinGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#0D9488" stopOpacity={0.18} />
                  <stop offset="95%" stopColor="#0D9488" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
              <XAxis dataKey="year" tick={{ fill: '#9CA3AF', fontSize: 11.5, fontWeight: 500 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#9CA3AF', fontSize: 11.5, fontWeight: 500 }} axisLine={false} tickLine={false}
                tickFormatter={v => `${v}km²`} width={50} />
              <Tooltip
                contentStyle={{
                  background: '#fff',
                  border: '1.5px solid rgba(17,24,39,0.1)',
                  borderRadius: 12, fontSize: 13,
                  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
                }}
                itemStyle={{ color: '#6B7280', fontWeight: 500 }}
                labelStyle={{ color: '#111827', fontWeight: 700 }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }} />
              <Area dataKey="target_area" name={targetCity.name}
                fill="url(#targetGrad)" stroke="#4338CA" strokeWidth={2.5} dot={false} connectNulls />
              <Area dataKey="twin_area" name={`${twinCity.name} (−${lagYears}yr)`}
                fill="url(#twinGrad)" stroke="#0D9488" strokeWidth={2.5} strokeDasharray="6 3" dot={false} connectNulls />
            </ComposedChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 8, textAlign: 'center' }}>
            Twin city timeline shifted back {lagYears} years for direct comparison
          </div>
        </div>
      )}

      {/* What happened to twin */}
      <div style={{
        background: 'var(--bg-base)',
        border: '1px solid var(--border-faint)',
        borderRadius: 14, padding: '16px 20px',
      }}>
        <div style={{ fontWeight: 700, fontSize: 13.5, color: 'var(--text-primary)', marginBottom: 14 }}>
          What happened to {twinCity.name}?
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
          {[
            {
              label: 'Land Price Growth',
              value: `${Math.round((twinCity.land_price_inr_per_sqft['2021'] / twinCity.land_price_inr_per_sqft['2010'] - 1) * 100)}%`,
              sub: `₹${twinCity.land_price_inr_per_sqft['2010'].toLocaleString()} → ₹${twinCity.land_price_inr_per_sqft['2021'].toLocaleString()}/sqft`,
              color: '#059669',
            },
            {
              label: 'Urban Area Expansion',
              value: `${((twinCity.urban_area_sqkm['2021'] / twinCity.urban_area_sqkm['2001']) * 1).toFixed(1)}×`,
              sub: `${twinCity.urban_area_sqkm['2001']} → ${twinCity.urban_area_sqkm['2021']} km²`,
              color: '#4338CA',
            },
            {
              label: 'Population Growth',
              value: `${Math.round((twinCity.population['2021'] / twinCity.population['2001'] - 1) * 100)}%`,
              sub: `${(twinCity.population['2001'] / 1e6).toFixed(2)}M → ${(twinCity.population['2021'] / 1e6).toFixed(2)}M`,
              color: '#D97706',
            },
          ].map(item => (
            <div key={item.label} style={{ textAlign: 'center' }}>
              <div className="stat-label" style={{ marginBottom: 5 }}>{item.label}</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: item.color, letterSpacing: '-0.4px', fontFamily: 'DM Sans, sans-serif' }}>{item.value}</div>
              <div style={{ fontSize: 11.5, color: '#9CA3AF', marginTop: 3 }}>{item.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
