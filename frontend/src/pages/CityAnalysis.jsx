import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, MapPin, TrendingUp, GitCompare, Loader2, Train, Plane, Landmark, GraduationCap, Cross, Route, Star } from 'lucide-react'
import { useWatchlist } from '../utils/watchlist'
import PredictionChart from '../components/PredictionChart'
import GrowthZoneMap from '../components/GrowthZoneMap'
import CityComparison from '../components/CityComparison'
import InvestmentScore from '../components/InvestmentScore'
import PersonaScore from '../components/PersonaScore'
import AiIntelligence from '../components/AiIntelligence'
import LiveAmenities from '../components/LiveAmenities'
import TimeMachine from '../components/TimeMachine'
import ProvenanceStrip from '../components/ProvenanceStrip'
import { fetchFullAnalysis, fetchSimilarCities, fetchZonePriceIndex, tierColor, phaseColor, formatPrice } from '../utils/api'

const TABS = [
  { id: 'prediction',  label: 'Growth Forecast' },
  { id: 'zones',       label: 'Investment Zones' },
  { id: 'ai',          label: 'AI Models' },
  { id: 'live',        label: 'Live (OSM)' },
  { id: 'twin',        label: 'Twin City' },
  { id: 'timemachine', label: 'Time Machine' },
  { id: 'similar',     label: 'Similar Cities' },
]

const INFRA_ICONS = {
  has_railway: Train,
  has_airport: Plane,
  has_university: GraduationCap,
  has_medical_college: Cross,
}

export default function CityAnalysis() {
  const { cityId }  = useParams()
  const navigate    = useNavigate()
  const { isWatched, toggle } = useWatchlist()
  const [data, setData]                 = useState(null)
  const [similar, setSimilar]           = useState([])
  const [zonePrice, setZonePrice]       = useState(null)
  const [zonePriceLoading, setZonePriceLoading] = useState(true)
  const [loading, setLoading]           = useState(true)
  const [error, setError]               = useState(null)
  const [activeTab, setActiveTab]       = useState('prediction')

  useEffect(() => {
    if (!cityId) return
    setLoading(true); setError(null); setData(null); setZonePrice(null); setZonePriceLoading(true)
    Promise.all([fetchFullAnalysis(cityId), fetchSimilarCities(cityId, 6)])
      .then(([analysis, sim]) => { setData(analysis); setSimilar(sim); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
    fetchZonePriceIndex(cityId)
      .then(z => { setZonePrice(z); setZonePriceLoading(false) })
      .catch(() => { setZonePrice(null); setZonePriceLoading(false) })
  }, [cityId])

  if (loading) return (
    <div style={{ minHeight: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.9, ease: 'linear' }}
      >
        <Loader2 size={32} color="var(--teal)" />
      </motion.div>
      <div style={{ color: '#9CA3AF', fontSize: 14, fontWeight: 500 }}>Loading city analysis…</div>
    </div>
  )

  if (error) return (
    <div style={{ maxWidth: 560, margin: '80px auto', textAlign: 'center', padding: '24px 20px' }}>
      <div style={{
        width: 64, height: 64, borderRadius: '50%',
        background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.2)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 20px',
      }}>
        <TrendingUp size={28} color="#F43F5E" />
      </div>
      <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>
        Could not load city data
      </div>
      <div style={{ color: '#9CA3AF', marginBottom: 20, fontSize: 14 }}>{error}</div>
      <button className="btn btn-outline" onClick={() => navigate('/')}>
        <ArrowLeft size={14} /> Back to Map
      </button>
    </div>
  )

  if (!data) return null
  const { city, history, prediction, twin } = data

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh' }}>
      <div style={{ maxWidth: 1340, margin: '0 auto', padding: '28px 24px 64px' }}>

        {/* ── Breadcrumb ── */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 24 }}
        >
          <motion.button
            whileHover={{ x: -2 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => navigate('/')}
            className="btn btn-outline"
            style={{ padding: '6px 13px', fontSize: 13, gap: 6, height: 36 }}
          >
            <ArrowLeft size={13} /> Map
          </motion.button>
          <span style={{ color: '#D1D5DB' }}>/</span>
          <span style={{ color: '#9CA3AF', fontSize: 13, fontWeight: 500 }}>{city.state}</span>
          <span style={{ color: '#D1D5DB' }}>/</span>
          <span style={{ fontWeight: 600, fontSize: 13, color: '#374151' }}>{city.name}</span>
        </motion.div>

        {/* ── City Header ── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.06, duration: 0.45 }}
          className="card"
          style={{ marginBottom: 24, overflow: 'hidden', position: 'relative' }}
        >
          {/* Gradient top strip */}
          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0, height: 4,
            background: `linear-gradient(90deg, ${tierColor(city.tier)}, ${phaseColor(city.growth_phase)})`,
          }} />

          <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap', alignItems: 'flex-start', paddingTop: 6 }}>
            {/* City info */}
            <div style={{ flex: 1, minWidth: 240 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, flexWrap: 'wrap' }}>
                <h1 style={{
                  fontSize: 30, fontWeight: 800, letterSpacing: '-0.6px',
                  color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif'
                }}>
                  {city.name}
                </h1>
                <span className={`badge badge-tier${city.tier}`}>Tier {city.tier}</span>
                <span className={`badge badge-${city.growth_phase}`} style={{ textTransform: 'capitalize' }}>
                  {city.growth_phase}
                </span>
                <motion.button
                  whileTap={{ scale: 0.92 }}
                  onClick={() => toggle(city.id)}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: 6,
                    padding: '5px 12px', borderRadius: 100, fontSize: 12.5, fontWeight: 600,
                    cursor: 'pointer', fontFamily: 'inherit',
                    background: isWatched(city.id) ? 'rgba(245,158,11,0.1)' : 'var(--bg-card)',
                    color: isWatched(city.id) ? '#D97706' : '#6B7280',
                    border: `1px solid ${isWatched(city.id) ? 'rgba(245,158,11,0.3)' : 'var(--border)'}`,
                  }}
                >
                  <Star size={13} fill={isWatched(city.id) ? '#D97706' : 'none'} strokeWidth={2} />
                  {isWatched(city.id) ? 'Watching' : 'Watch'}
                </motion.button>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#9CA3AF', fontSize: 14, marginBottom: 14 }}>
                <MapPin size={13} />
                {city.state}
              </div>
              <p style={{ fontSize: 14.5, color: '#6B7280', lineHeight: 1.7, maxWidth: 520 }}>
                {city.description}
              </p>
            </div>

            {/* Quick stats */}
            <div className="grid-4" style={{ gap: 12, flex: '0 1 520px', minWidth: 0 }}>
              {[
                {
                  label: 'Population 2021',
                  value: `${(city.population['2021'] / 1e6).toFixed(2)}M`,
                  sub: `+${Math.round((city.population['2021'] / city.population['2001'] - 1) * 100)}% since 2001`,
                },
                {
                  label: 'Urban Area',
                  value: `${city.urban_area_sqkm['2021']} km²`,
                  sub: `was ${city.urban_area_sqkm['2001']} km² in 2001`,
                },
                {
                  label: 'Land Price',
                  value: `₹${city.land_price_inr_per_sqft['2021'].toLocaleString()}`,
                  sub: 'per sq ft · 2021',
                },
                {
                  label: 'Investment Score',
                  value: city.investment_score,
                  sub: `${city.growth_phase} phase`,
                },
              ].map(({ label, value, sub }) => (
                <div key={label} style={{
                  background: 'var(--bg-base)',
                  border: '1px solid var(--border-faint)',
                  borderRadius: 13, padding: '13px 15px',
                }}>
                  <div className="stat-label">{label}</div>
                  <div className="stat-value" style={{ fontSize: 18 }}>{value}</div>
                  <div className="stat-sub">{sub}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Infrastructure tags */}
          <div className="divider" />
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
            <span style={{ fontSize: 11.5, color: '#9CA3AF', marginRight: 4, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Infrastructure
            </span>
            {city.infrastructure.has_railway && (
              <span className="tag"><Train size={11} strokeWidth={2} /> Railway</span>
            )}
            {city.infrastructure.has_airport && (
              <span className="tag"><Plane size={11} strokeWidth={2} /> Airport</span>
            )}
            {city.infrastructure.num_national_highways > 0 && (
              <span className="tag"><Route size={11} strokeWidth={2} /> {city.infrastructure.num_national_highways} NH</span>
            )}
            {city.infrastructure.has_university && (
              <span className="tag"><GraduationCap size={11} strokeWidth={2} /> University</span>
            )}
            {city.infrastructure.has_medical_college && (
              <span className="tag"><Cross size={11} strokeWidth={2} /> Medical College</span>
            )}
            {city.government_schemes.map(s => (
              <span key={s} className="tag" style={{
                background: 'rgba(67, 56, 202, 0.07)',
                color: 'var(--indigo)',
                borderColor: 'rgba(67, 56, 202, 0.16)',
              }}>
                <Landmark size={11} strokeWidth={2} /> {s}
              </span>
            ))}
            <span style={{ marginLeft: 'auto', fontSize: 12.5, color: '#9CA3AF', fontWeight: 500 }}>
              Nearest metro: <strong style={{ color: '#374151' }}>{city.nearest_metro}</strong>
              {' '}({city.dist_to_metro_km} km)
            </span>
          </div>
        </motion.div>

        {/* ── Main 2-col layout ── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 330px', gap: 22, alignItems: 'start' }}
          className="city-analysis-grid">
          <style>{`@media(max-width:900px){.city-analysis-grid{grid-template-columns:1fr!important}}`}</style>

          {/* Left: tabbed content */}
          <div>
            {/* Tab bar */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.35 }}
              style={{
                display: 'flex', gap: 4, marginBottom: 16,
                background: 'var(--bg-card)',
                border: '1px solid var(--border-faint)',
                padding: '5px', borderRadius: 14,
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              {TABS.map(tab => (
                <button key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    flex: 1, padding: '8px 10px', borderRadius: 10, border: 'none',
                    fontSize: 13.5, fontWeight: 500, transition: 'all 0.18s',
                    background: activeTab === tab.id
                      ? 'linear-gradient(135deg, #4338CA, #0D9488)'
                      : 'transparent',
                    color: activeTab === tab.id ? '#fff' : '#9CA3AF',
                    boxShadow: activeTab === tab.id
                      ? '0 2px 12px rgba(67, 56, 202, 0.25)'
                      : 'none',
                    cursor: 'pointer',
                    fontFamily: 'inherit',
                  }}>
                  {tab.label}
                </button>
              ))}
            </motion.div>

            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.22 }}
                className="card"
              >
                {activeTab === 'prediction' && (
                  <>
                    <PredictionChart history={history} prediction={prediction} />
                    <div style={{ marginTop: 16 }}>
                      <ProvenanceStrip kind="heuristic" provenance={{ source: 'Phase-based growth forecast' }} note="Bounded phase-based CAGR + infrastructure multipliers (prediction_engine). Confidence bands are formulaic, not statistical — the XGBoost conformal interval is on the AI Models tab." />
                    </div>
                  </>
                )}

                {activeTab === 'zones' && (
                  <div>
                    <GrowthZoneMap city={city} zones={prediction?.investment_zones || []} height={380} />
                    <div style={{ marginTop: 22 }}>
                      <div className="section-title">Zone Investment Details</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        {(prediction?.investment_zones || []).filter(z => z.horizon_years === 5).map(zone => (
                          <div key={zone.zone_id} style={{
                            background: 'var(--bg-base)',
                            border: '1px solid var(--border-faint)',
                            borderRadius: 13, padding: '14px 18px',
                            display: 'flex', gap: 14, alignItems: 'center',
                          }}>
                            <div style={{
                              width: 44, height: 44, borderRadius: 12, flexShrink: 0,
                              background: 'rgba(5, 150, 105, 0.08)',
                              border: '1px solid rgba(5, 150, 105, 0.18)',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                              <MapPin size={18} color="#059669" strokeWidth={2} />
                            </div>
                            <div style={{ flex: 1 }}>
                              <div style={{ fontWeight: 600, fontSize: 14.5, marginBottom: 3, color: 'var(--text-primary)' }}>{zone.label}</div>
                              <div style={{ fontSize: 12.5, color: '#9CA3AF' }}>
                                Radius: ~{zone.radius_km} km beyond current boundary
                              </div>
                            </div>
                            <div style={{ textAlign: 'right', flexShrink: 0 }}>
                              <div style={{ fontSize: 10.5, color: '#9CA3AF', marginBottom: 3, fontWeight: 500 }}>Expected Rise</div>
                              <div style={{ fontWeight: 800, fontSize: 18, color: '#059669', fontFamily: 'DM Sans, sans-serif' }}>
                                +{zone.expected_price_rise_pct}%
                              </div>
                            </div>
                            <div style={{
                              padding: '6px 13px', borderRadius: 9, fontSize: 12.5, fontWeight: 600, flexShrink: 0,
                              background: zone.recommendation === 'Buy Now'
                                ? 'rgba(5,150,105,0.08)' : 'rgba(67,56,202,0.08)',
                              color: zone.recommendation === 'Buy Now'
                                ? '#059669' : 'var(--indigo)',
                              border: zone.recommendation === 'Buy Now'
                                ? '1px solid rgba(5,150,105,0.2)' : '1px solid rgba(67,56,202,0.2)',
                            }}>
                              {zone.recommendation}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {zonePrice?.zones?.length > 0 && (
                      <div style={{ marginTop: 24 }}>
                        <div className="section-title">Land Price Index by Zone</div>
                        <div style={{ fontSize: 12.5, color: '#9CA3AF', marginBottom: 12 }}>
                          Per-corridor price off the city core (₹{zonePrice.core_price_inr_per_sqft.toLocaleString()}/sqft) — entry price today, projected price, and implied appreciation.
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
                            <thead>
                              <tr style={{ textAlign: 'left', color: '#9CA3AF', fontWeight: 600 }}>
                                {['Zone', 'Today', 'Projected', 'Implied CAGR', 'Disc. to core'].map((h, i) => (
                                  <th key={h} style={{ padding: '7px 10px', borderBottom: '1px solid var(--border-faint)', textAlign: i === 0 ? 'left' : 'right' }}>{h}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {zonePrice.zones.map(z => {
                                const cheapest = z.zone_id === zonePrice.cheapest_zone_id
                                const hottest = z.zone_id === zonePrice.highest_appreciation_zone_id
                                return (
                                  <tr key={z.zone_id}>
                                    <td style={{ padding: '9px 10px', borderBottom: '1px solid var(--border-faint)', fontWeight: 600, color: 'var(--text-primary)' }}>
                                      {z.label}
                                      {cheapest && <span style={{ marginLeft: 6, fontSize: 10, color: '#059669', background: 'rgba(5,150,105,0.1)', padding: '1px 7px', borderRadius: 100 }}>cheapest</span>}
                                      {hottest && <span style={{ marginLeft: 6, fontSize: 10, color: '#D97706', background: 'rgba(245,158,11,0.12)', padding: '1px 7px', borderRadius: 100 }}>hottest</span>}
                                    </td>
                                    <td style={{ padding: '9px 10px', borderBottom: '1px solid var(--border-faint)', textAlign: 'right', color: '#374151' }}>{formatPrice(z.current_price_inr_per_sqft)}</td>
                                    <td style={{ padding: '9px 10px', borderBottom: '1px solid var(--border-faint)', textAlign: 'right', color: '#374151' }}>{formatPrice(z.projected_price_inr_per_sqft)}</td>
                                    <td style={{ padding: '9px 10px', borderBottom: '1px solid var(--border-faint)', textAlign: 'right', fontWeight: 700, color: '#059669' }}>{z.implied_price_cagr_pct}%</td>
                                    <td style={{ padding: '9px 10px', borderBottom: '1px solid var(--border-faint)', textAlign: 'right', color: '#9CA3AF' }}>−{z.discount_to_core_pct}%</td>
                                  </tr>
                                )
                              })}
                            </tbody>
                          </table>
                        </div>
                        <div style={{ marginTop: 12 }}>
                          <ProvenanceStrip kind="heuristic" provenance={{ source: 'Zone price index' }} note={zonePrice.method} />
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'ai' && (
                  <AiIntelligence cityId={cityId} city={city} />
                )}

                {activeTab === 'timemachine' && (
                  <TimeMachine cityId={cityId} />
                )}

                {activeTab === 'live' && (
                  <LiveAmenities cityId={cityId} />
                )}

                {activeTab === 'twin' && (
                  <CityComparison targetCity={city} twin={twin} />
                )}

                {activeTab === 'similar' && (
                  <div>
                    <div className="section-title">Cities with Similar Growth DNA</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                      {similar.map(sc => {
                        const pc = phaseColor(sc.growth_phase)
                        return (
                          <motion.button key={sc.city_id}
                            whileHover={{ y: -3, boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => navigate(`/city/${sc.city_id}`)}
                            style={{
                              textAlign: 'left', background: 'var(--bg-base)',
                              border: '1px solid var(--border-faint)',
                              borderRadius: 13, padding: '14px',
                              cursor: 'pointer', fontFamily: 'inherit',
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 5 }}>
                              <span style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>{sc.name}</span>
                              <span style={{
                                fontSize: 11.5, color: 'var(--indigo)', fontWeight: 700,
                                background: 'rgba(67,56,202,0.08)', padding: '2px 8px', borderRadius: 100,
                                border: '1px solid rgba(67,56,202,0.16)',
                              }}>
                                {sc.similarity_score}%
                              </span>
                            </div>
                            <div style={{ fontSize: 12.5, color: '#9CA3AF', marginBottom: 11, fontWeight: 500 }}>
                              {sc.state} · Tier {sc.tier}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{
                                background: `${pc}10`, color: pc, border: `1px solid ${pc}20`,
                                padding: '2px 9px', borderRadius: 100,
                                fontSize: 11, fontWeight: 600, textTransform: 'capitalize',
                              }}>{sc.growth_phase}</span>
                              <span style={{ fontSize: 15, fontWeight: 800, color: '#059669', fontFamily: 'DM Sans, sans-serif' }}>
                                {sc.investment_score}
                              </span>
                            </div>
                          </motion.button>
                        )
                      })}
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Right: score + compare CTA */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.45 }}
            style={{ display: 'flex', flexDirection: 'column', gap: 14 }}
          >
            <div className="card">
              <div className="section-title">
                <TrendingUp size={13} />
                Investment Intelligence
              </div>
              <InvestmentScore
                city={city}
                prediction={prediction}
                zonePriceData={zonePrice}
                zonePriceLoading={zonePriceLoading}
                subscriptionTier="developer"
              />
              <div style={{ marginTop: 14 }}>
                <ProvenanceStrip kind="heuristic" provenance={{ source: 'Weighted investment scoring' }} note="Heuristic weighted sub-scores + curated inputs. Directional, not investment advice." />
              </div>
            </div>

            <PersonaScore cityId={cityId} />

            {twin && (
              <Link to={`/compare?a=${cityId}&b=${twin.city_id}`}>
                <motion.div
                  whileHover={{ scale: 1.01, borderColor: 'rgba(67,56,202,0.35)' }}
                  whileTap={{ scale: 0.99 }}
                  style={{
                    background: 'rgba(67, 56, 202, 0.04)',
                    border: '1px solid rgba(67, 56, 202, 0.16)',
                    borderRadius: 16, padding: '16px 18px',
                    cursor: 'pointer', transition: 'all 0.2s',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 7 }}>
                    <GitCompare size={16} color="var(--indigo)" />
                    <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--indigo)' }}>
                      Compare with Twin City
                    </span>
                  </div>
                  <div style={{ fontSize: 13, color: '#6B7280', lineHeight: 1.6 }}>
                    See {twin.twin_city?.name || ''}'s growth trajectory and how it predicts{' '}
                    {city.name}'s future →
                  </div>
                </motion.div>
              </Link>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
}
