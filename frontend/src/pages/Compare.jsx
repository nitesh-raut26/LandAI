import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { GitCompare, Loader2, ArrowRightLeft } from 'lucide-react'
import CitySearch from '../components/CitySearch'
import PredictionChart from '../components/PredictionChart'
import InvestmentScore from '../components/InvestmentScore'
import { fetchFullAnalysis, getAuthToken, recordCompareApi, tierColor, phaseColor } from '../utils/api'

export default function Compare() {
  const [sp] = useSearchParams()
  const [dataA, setDataA] = useState(null)
  const [dataB, setDataB] = useState(null)
  const [loadingA, setLoadingA] = useState(false)
  const [loadingB, setLoadingB] = useState(false)

  const loadCity = (id, setter, setLoading) => {
    if (!id) return
    setLoading(true)
    fetchFullAnalysis(id)
      .then(d => { setter(d); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => {
    const a = sp.get('a'), b = sp.get('b')
    if (a) loadCity(a, setDataA, setLoadingA)
    if (b) loadCity(b, setDataB, setLoadingB)
  }, [])

  // Record each completed comparison for signed-in users (best-effort; the
  // backend collapses immediate duplicates so re-renders won't spam history).
  useEffect(() => {
    const a = dataA?.city?.id, b = dataB?.city?.id
    if (a && b && getAuthToken()) recordCompareApi(a, b).catch(() => {})
  }, [dataA?.city?.id, dataB?.city?.id])

  const ACCENT_A = '#4338CA'   // indigo
  const ACCENT_B = '#0D9488'   // teal

  const CityPanel = ({ data, loading, label, accentColor, onSelect }) => (
    <div style={{ flex: 1, minWidth: 0 }}>
      <div style={{
        fontSize: 10.5, color: '#9CA3AF', textTransform: 'uppercase',
        letterSpacing: '0.8px', fontWeight: 600, marginBottom: 11,
        display: 'flex', alignItems: 'center', gap: 7,
      }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: accentColor, display: 'inline-block', flexShrink: 0 }} />
        {label}
      </div>
      <CitySearch placeholder="Search city…" onSelect={onSelect} compact />

      {loading && (
        <div style={{ marginTop: 40, display: 'flex', justifyContent: 'center' }}>
          <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 0.9, ease: 'linear' }}>
            <Loader2 size={24} color={accentColor} />
          </motion.div>
        </div>
      )}

      {data && !loading && (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 14 }}
          >
            {/* City header */}
            <div style={{
              background: 'var(--bg-base)',
              border: `1.5px solid ${accentColor}20`,
              borderTop: `3px solid ${accentColor}`,
              borderRadius: 14, padding: '16px 18px',
            }}>
              <div style={{ fontWeight: 800, fontSize: 22, marginBottom: 3, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>
                {data.city.name}
              </div>
              <div style={{ fontSize: 13, color: '#9CA3AF', marginBottom: 12, fontWeight: 500 }}>{data.city.state}</div>
              <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
                <span style={{
                  background: `${tierColor(data.city.tier)}10`,
                  color: tierColor(data.city.tier),
                  border: `1px solid ${tierColor(data.city.tier)}20`,
                  padding: '2px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600,
                }}>Tier {data.city.tier}</span>
                <span style={{
                  background: `${phaseColor(data.city.growth_phase)}10`,
                  color: phaseColor(data.city.growth_phase),
                  border: `1px solid ${phaseColor(data.city.growth_phase)}20`,
                  padding: '2px 10px', borderRadius: 100, fontSize: 11, fontWeight: 600,
                  textTransform: 'capitalize',
                }}>{data.city.growth_phase}</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {[
                  { l: 'Population 2021', v: `${(data.city.population['2021'] / 1e6).toFixed(2)}M` },
                  { l: 'Urban Area',      v: `${data.city.urban_area_sqkm['2021']} km²` },
                  { l: 'Land Price',      v: `₹${data.city.land_price_inr_per_sqft['2021'].toLocaleString()}/sqft` },
                  { l: 'Inv. Score',      v: data.city.investment_score },
                ].map(({ l, v }) => (
                  <div key={l}>
                    <div style={{ fontSize: 10.5, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 2, fontWeight: 500 }}>
                      {l}
                    </div>
                    <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>{v}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-sm">
              <InvestmentScore city={data.city} prediction={data.prediction} />
            </div>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  )

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh' }}>
      <div style={{ maxWidth: 1340, margin: '0 auto', padding: '36px 24px 64px' }}>

        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          style={{ marginBottom: 36 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 13, marginBottom: 10 }}>
            <div style={{
              width: 46, height: 46, borderRadius: 13,
              background: 'linear-gradient(135deg, rgba(67,56,202,0.1), rgba(13,148,136,0.1))',
              border: '1px solid rgba(67,56,202,0.18)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <GitCompare size={20} color="var(--indigo)" />
            </div>
            <h1 style={{
              fontSize: 28, fontWeight: 800, letterSpacing: '-0.5px',
              fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)',
            }}>City Comparison</h1>
          </div>
          <p style={{ color: '#9CA3AF', fontSize: 14.5, fontWeight: 400 }}>
            Select any two cities to compare growth trajectories, land price forecasts, and investment scores side by side.
          </p>
        </motion.div>

        {/* City selector panels */}
        <motion.div
          className="compare-selectors"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
          style={{ marginBottom: 28 }}
        >
          <div className="card">
            <CityPanel data={dataA} loading={loadingA} label="City A" accentColor={ACCENT_A}
              onSelect={c => loadCity(c.id, setDataA, setLoadingA)} />
          </div>

          <div className="compare-swap" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '64px 18px 0' }}>
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ repeat: Infinity, repeatDelay: 3, duration: 0.6 }}
              style={{
                width: 40, height: 40, borderRadius: '50%',
                background: 'var(--bg-card)',
                border: '1.5px solid var(--border)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: 'var(--shadow-md)',
              }}
            >
              <ArrowRightLeft size={15} color="#9CA3AF" />
            </motion.div>
          </div>

          <div className="card">
            <CityPanel data={dataB} loading={loadingB} label="City B" accentColor={ACCENT_B}
              onSelect={c => loadCity(c.id, setDataB, setLoadingB)} />
          </div>
        </motion.div>

        {/* Side-by-side charts */}
        <AnimatePresence>
          {dataA && dataB && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
              style={{ display: 'flex', flexDirection: 'column', gap: 20 }}
            >
              <div className="grid-2" style={{ gap: 20 }}>
                <div className="card">
                  <div className="section-title" style={{ color: ACCENT_A }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: ACCENT_A, flexShrink: 0 }} />
                    {dataA.city.name} — Growth Forecast
                  </div>
                  <PredictionChart history={dataA.history} prediction={dataA.prediction} />
                </div>
                <div className="card">
                  <div className="section-title" style={{ color: ACCENT_B }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: ACCENT_B, flexShrink: 0 }} />
                    {dataB.city.name} — Growth Forecast
                  </div>
                  <PredictionChart history={dataB.history} prediction={dataB.prediction} />
                </div>
              </div>

              {/* Head-to-head table */}
              <div className="card">
                <div className="section-title">Head-to-Head Metrics</div>
                <div className="scroll-x">
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13.5 }}>
                    <thead>
                      <tr style={{ borderBottom: '1.5px solid var(--border-faint)' }}>
                        <th style={{ textAlign: 'left', padding: '11px 16px', color: '#9CA3AF', fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                          Metric
                        </th>
                        <th style={{ textAlign: 'center', padding: '11px 16px', color: ACCENT_A, fontWeight: 700 }}>
                          {dataA.city.name}
                        </th>
                        <th style={{ textAlign: 'center', padding: '11px 16px', color: ACCENT_B, fontWeight: 700 }}>
                          {dataB.city.name}
                        </th>
                        <th style={{ textAlign: 'center', padding: '11px 16px', color: '#9CA3AF', fontWeight: 500 }}>
                          Better
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { metric: 'Investment Score',    valA: dataA.city.investment_score,                        valB: dataB.city.investment_score,                        fmt: v => v,         higher: true  },
                        { metric: 'Current Land Price',  valA: dataA.city.land_price_inr_per_sqft['2021'],         valB: dataB.city.land_price_inr_per_sqft['2021'],         fmt: v => `₹${v.toLocaleString()}/sqft`, higher: false },
                        { metric: 'Annual Price CAGR',   valA: dataA.prediction?.annual_cagr_price_pct,            valB: dataB.prediction?.annual_cagr_price_pct,            fmt: v => `${v}%`,   higher: true  },
                        { metric: '5-Year Price Rise',   valA: dataA.prediction?.milestones?.price_appreciation_5yr_pct,  valB: dataB.prediction?.milestones?.price_appreciation_5yr_pct,  fmt: v => `+${v}%`, higher: true },
                        { metric: '10-Year Price Rise',  valA: dataA.prediction?.milestones?.price_appreciation_10yr_pct, valB: dataB.prediction?.milestones?.price_appreciation_10yr_pct, fmt: v => `+${v}%`, higher: true },
                        { metric: 'Urban Area 2031',     valA: dataA.prediction?.milestones?.area_2031_sqkm,       valB: dataB.prediction?.milestones?.area_2031_sqkm,       fmt: v => `${v} km²`, higher: true },
                        { metric: 'Infrastructure',      valA: dataA.city.scores.infrastructure,                  valB: dataB.city.scores.infrastructure,                  fmt: v => v,          higher: true },
                        { metric: 'Economic Activity',   valA: dataA.city.scores.economic_activity,               valB: dataB.city.scores.economic_activity,               fmt: v => v,          higher: true },
                      ].map(({ metric, valA, valB, fmt, higher }, i) => {
                        const aWins = higher ? valA > valB : valA < valB
                        const bWins = higher ? valB > valA : valB < valA
                        return (
                          <tr key={metric} style={{
                            borderBottom: '1px solid var(--border-faint)',
                            background: i % 2 === 0 ? 'transparent' : 'rgba(0,0,0,0.015)',
                            transition: 'background 0.12s',
                          }}>
                            <td style={{ padding: '11px 16px', color: '#6B7280', fontSize: 13.5, fontWeight: 500 }}>{metric}</td>
                            <td style={{ padding: '11px 16px', textAlign: 'center', fontWeight: 600, color: aWins ? '#059669' : 'var(--text-primary)' }}>
                              {valA != null ? fmt(valA) : '—'}
                            </td>
                            <td style={{ padding: '11px 16px', textAlign: 'center', fontWeight: 600, color: bWins ? '#059669' : 'var(--text-primary)' }}>
                              {valB != null ? fmt(valB) : '—'}
                            </td>
                            <td style={{ padding: '11px 16px', textAlign: 'center' }}>
                              {aWins && <span style={{ color: ACCENT_A, fontWeight: 700, fontSize: 12.5 }}>{dataA.city.name}</span>}
                              {bWins && <span style={{ color: ACCENT_B, fontWeight: 700, fontSize: 12.5 }}>{dataB.city.name}</span>}
                              {!aWins && !bWins && <span style={{ color: '#9CA3AF', fontSize: 12 }}>Tie</span>}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty state */}
        {(!dataA || !dataB) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            style={{ padding: '72px 20px', textAlign: 'center', color: '#9CA3AF' }}
          >
            <div style={{
              width: 72, height: 72, borderRadius: '50%',
              background: 'linear-gradient(135deg, rgba(67,56,202,0.07), rgba(13,148,136,0.07))',
              border: '1.5px solid var(--border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 22px',
              boxShadow: 'var(--shadow-md)',
            }}>
              <GitCompare size={30} color="#9CA3AF" />
            </div>
            <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8, color: '#374151', fontFamily: 'DM Sans, sans-serif' }}>
              Select two cities to begin comparison
            </div>
            <div style={{ fontSize: 14, color: '#9CA3AF', fontWeight: 400 }}>
              Try: Jhanjharpur vs Darbhanga, or Tirupati vs Warangal
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
