import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { TrendingUp, MapPin, Building, BarChart2, ArrowRight, Zap, Cpu, Navigation, Star, Bookmark, Check } from 'lucide-react'
import MapView from '../components/MapView'
import CitySearch from '../components/CitySearch'
import CustomSelect from '../components/CustomSelect'
import CopilotBox from '../components/CopilotBox'
import { fetchAllCities, tierColor, phaseColor, fetchStates, getAuthToken, saveSearchApi } from '../utils/api'
import { useWatchlist } from '../utils/watchlist'

const HIGHLIGHT_CITIES = [
  'jhanjharpur', 'tirupati', 'raipur', 'bhubaneswar',
  'siliguri', 'warangal', 'kota', 'jamnagar',
]

const fadeUp = {
  hidden:  { opacity: 0, y: 20 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.48, ease: [0.22, 1, 0.36, 1] } }),
}

export default function Home() {
  const [cities, setCities] = useState([])
  const [states, setStates] = useState([])
  const [filterState, setFilterState] = useState('')
  const [filterTier, setFilterTier] = useState('')
  const [filterPhase, setFilterPhase] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [sortBy, setSortBy] = useState('score')
  const [loading, setLoading] = useState(true)
  const { ids: watchIds, toggle: toggleWatch } = useWatchlist()
  const [coords, setCoords] = useState(null)
  const [geoStatus, setGeoStatus] = useState('idle') // idle | locating | ok | denied | unsupported
  const navigate = useNavigate()
  const [sp] = useSearchParams()
  const [savedSearch, setSavedSearch] = useState(false)

  // Seed filters from the URL (?state=&tier=&phase=) so a saved search "Run"
  // lands here with its filters applied.
  useEffect(() => {
    const s = sp.get('state'); if (s) setFilterState(s)
    const t = sp.get('tier'); if (t) setFilterTier(t)
    const p = sp.get('phase'); if (p) setFilterPhase(p)
  }, []) // eslint-disable-line

  useEffect(() => {
    Promise.all([fetchAllCities(), fetchStates()])
      .then(([c, s]) => {
        setCities(Array.isArray(c) ? c : [])
        setStates(Array.isArray(s) ? s : [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  // Ask for the visitor's location to surface nearby cities first
  useEffect(() => {
    if (!('geolocation' in navigator)) { setGeoStatus('unsupported'); return }
    setGeoStatus('locating')
    navigator.geolocation.getCurrentPosition(
      pos => { setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude }); setGeoStatus('ok') },
      () => setGeoStatus('denied'),
      { timeout: 8000, maximumAge: 600000 },
    )
  }, [])

  const withDistance = useMemo(() => {
    if (!coords || !cities.length) return []
    const R = 6371, rad = Math.PI / 180
    const dist = (la, ln) => {
      const dLat = (la - coords.lat) * rad, dLng = (ln - coords.lng) * rad
      const x = Math.sin(dLat / 2) ** 2 + Math.cos(coords.lat * rad) * Math.cos(la * rad) * Math.sin(dLng / 2) ** 2
      return 2 * R * Math.asin(Math.sqrt(x))
    }
    return cities
      .map(c => ({ ...c, distance_km: Math.round(dist(c.lat, c.lng) * 10) / 10 }))
      .sort((a, b) => a.distance_km - b.distance_km)
  }, [coords, cities])

  const nearby = withDistance.slice(0, 6)               // closest by distance
  // Best-scoring cities among the ~16 nearest → "top opportunities near you".
  const nearbyByScore = useMemo(
    () => [...withDistance.slice(0, 16)].sort((a, b) => b.investment_score - a.investment_score).slice(0, 8),
    [withDistance],
  )
  const detectedRegion = nearby[0]?.state || null
  const nearestCity = nearby[0] || null
  const watched = cities.filter(c => watchIds.includes(c.id))

  const filtered = cities
    .filter(c =>
      (!filterState || c.state === filterState) &&
      (!filterTier || c.tier === Number(filterTier)) &&
      (!filterPhase || c.growth_phase === filterPhase) &&
      (!maxPrice || c.land_price_inr_per_sqft['2021'] <= Number(maxPrice))
    )
    .sort((a, b) => {
      if (sortBy === 'price') return a.land_price_inr_per_sqft['2021'] - b.land_price_inr_per_sqft['2021']
      if (sortBy === 'name') return a.name.localeCompare(b.name)
      // 'score' (default) and 'growth' both rank by investment score desc
      return b.investment_score - a.investment_score
    })

  const anyFilter = filterState || filterTier || filterPhase || maxPrice

  const highlights = cities.filter(c => HIGHLIGHT_CITIES.includes(c.id))
  // When the visitor shares location, surface the best-scoring nearby cities as
  // the headline opportunities; otherwise fall back to the curated highlight set.
  const gpsOn = geoStatus === 'ok' && nearbyByScore.length > 0
  const topOpportunities = gpsOn ? nearbyByScore : highlights
  const tierCounts = [1, 2, 3].map(t => ({ tier: t, count: cities.filter(c => c.tier === t).length }))
  const phaseCounts = ['emerging', 'accelerating', 'maturing', 'mature'].map(ph => ({
    phase: ph, count: cities.filter(c => c.growth_phase === ph).length,
  }))

  const STATS = [
    { label: 'Cities Tracked',    value: cities.length,                                           color: '#4338CA', bg: 'rgba(67,56,202,0.07)',  border: 'rgba(67,56,202,0.14)',  icon: MapPin     },
    { label: 'Indian States',     value: states.length,                                           color: '#0D9488', bg: 'rgba(13,148,136,0.07)', border: 'rgba(13,148,136,0.14)', icon: Building   },
    { label: 'Emerging Cities',   value: cities.filter(c => c.growth_phase === 'emerging').length, color: '#059669', bg: 'rgba(5,150,105,0.07)',  border: 'rgba(5,150,105,0.14)',  icon: TrendingUp },
    {
      label: 'Avg Investment Score',
      value: cities.length ? Math.round(cities.reduce((s, c) => s + c.investment_score, 0) / cities.length) : 0,
      color: '#D97706', bg: 'rgba(245,158,11,0.07)', border: 'rgba(245,158,11,0.14)', icon: BarChart2,
    },
  ]

  const stateOptions = [
    { value: '', label: 'All States' },
    ...states.map(s => ({ value: s, label: s })),
  ]
  const tierOptions = [
    { value: '', label: 'All Tiers' },
    { value: '1', label: 'Tier 1 — Metro' },
    { value: '2', label: 'Tier 2 — Growing' },
    { value: '3', label: 'Tier 3 — Emerging' },
  ]
  const phaseOptions = [
    { value: '', label: 'All Phases' },
    { value: 'emerging', label: 'Emerging' },
    { value: 'accelerating', label: 'Accelerating' },
    { value: 'maturing', label: 'Maturing' },
    { value: 'mature', label: 'Mature' },
  ]
  const priceOptions = [
    { value: '', label: 'Any Budget' },
    { value: '1000', label: '≤ ₹1,000/sqft' },
    { value: '2000', label: '≤ ₹2,000/sqft' },
    { value: '3500', label: '≤ ₹3,500/sqft' },
    { value: '6000', label: '≤ ₹6,000/sqft' },
  ]
  const sortOptions = [
    { value: 'score', label: 'Sort: Investment Score' },
    { value: 'price', label: 'Sort: Price (low→high)' },
    { value: 'name', label: 'Sort: Name (A→Z)' },
  ]

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh' }}>
      {/* ── Hero Section ── */}
      <div style={{ position: 'relative', overflow: 'hidden', isolation: 'isolate' }}>
        {/* Hero Background Image */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'url(/hero-bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center top',
          zIndex: 0,
        }} />
        {/* Gradient overlay */}
        <div style={{
          position: 'absolute', inset: 0, zIndex: 1,
          background: 'linear-gradient(180deg, rgba(245,243,239,0.65) 0%, rgba(245,243,239,0.92) 55%, rgba(245,243,239,1) 100%)',
        }} />

        <div style={{ position: 'relative', zIndex: 2, maxWidth: 1340, margin: '0 auto', padding: '72px 24px 64px' }}>
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            style={{ display: 'flex', justifyContent: 'center', marginBottom: 28 }}
          >
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: 'rgba(255,255,255,0.82)',
              border: '1px solid rgba(13, 148, 136, 0.22)',
              borderRadius: 100, padding: '7px 18px',
              fontSize: 12.5, color: '#0F766E', fontWeight: 600,
              boxShadow: '0 2px 12px rgba(13,148,136,0.1)',
              backdropFilter: 'blur(12px)',
            }}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%',
                background: '#059669',
                display: 'inline-block',
                boxShadow: '0 0 0 3px rgba(5,150,105,0.25)',
              }} />
              AI-Powered · {loading ? '…' : cities.length} Cities · {loading ? '…' : states.length} States · Predictive
            </div>
          </motion.div>

          {/* Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
            style={{
              textAlign: 'center',
              fontFamily: 'DM Sans, Inter, sans-serif',
              fontSize: 'clamp(32px, 5.5vw, 58px)',
              fontWeight: 800,
              letterSpacing: '-1.5px',
              lineHeight: 1.12,
              marginBottom: 20,
              color: '#111827',
            }}
          >
            Predict Where India's{' '}
            <span className="text-gradient">Land Value</span>
            {' '}Will Rise
          </motion.h1>

          {/* Sub */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.16, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            style={{
              textAlign: 'center',
              fontSize: 17, color: '#6B7280',
              maxWidth: 560, margin: '0 auto 36px',
              lineHeight: 1.75, fontWeight: 400,
            }}
          >
            Compare Tier 3 cities with historically similar Tier 2 cities.
            Discover zones that develop in 5–10 years before prices explode.
          </motion.p>

          {/* Search */}
          <motion.div
            initial={{ opacity: 0, y: 14, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.22, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            style={{ maxWidth: 520, margin: '0 auto' }}
          >
            <CitySearch placeholder={nearestCity ? `Search near ${nearestCity.name} — or any Indian city…` : 'Search Jhanjharpur, Tirupati, Raipur...'} />
          </motion.div>
        </div>
      </div>

      {/* ── Content ── */}
      <div style={{ maxWidth: 1340, margin: '0 auto', padding: '0 24px 64px' }}>

        {/* ── Stats bar ── */}
        <div className="grid-4" style={{ marginBottom: 36, marginTop: -24, position: 'relative', zIndex: 1 }}>
          {STATS.map(({ label, value, color, bg, border, icon: Icon }, i) => (
            <motion.div
              key={label}
              custom={i}
              variants={fadeUp}
              initial="hidden"
              animate="visible"
              whileHover={{ y: -4, boxShadow: '0 12px 40px rgba(0,0,0,0.1)' }}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-faint)',
                borderRadius: 18,
                padding: '18px 20px',
                display: 'flex', alignItems: 'center', gap: 14,
                boxShadow: 'var(--shadow-sm)',
                cursor: 'default',
              }}
            >
              <div style={{
                width: 48, height: 48, borderRadius: 14, flexShrink: 0,
                background: bg, border: `1px solid ${border}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon size={20} color={color} strokeWidth={2} />
              </div>
              <div>
                <div style={{ fontSize: 26, fontWeight: 800, color, letterSpacing: '-0.6px', lineHeight: 1, fontFamily: 'DM Sans, sans-serif' }}>
                  {loading ? '—' : value}
                </div>
                <div style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4, fontWeight: 500 }}>{label}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* ── AI Copilot ── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          style={{ marginBottom: 36 }}
        >
          <CopilotBox />
        </motion.div>

        {/* ── My Watchlist ── */}
        {watched.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 36 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <div style={{ width: 32, height: 32, borderRadius: 9, background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.22)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Star size={15} color="#D97706" fill="#D97706" strokeWidth={2} />
              </div>
              <span style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>My Watchlist</span>
              <span style={{ marginLeft: 'auto', fontSize: 12.5, color: '#9CA3AF', fontWeight: 500 }}>{watched.length} saved</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 12 }}>
              {watched.map(city => {
                const pc = phaseColor(city.growth_phase)
                return (
                  <div key={city.id} style={{ position: 'relative', background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 16, padding: '15px 16px', boxShadow: 'var(--shadow-sm)' }}>
                    <button onClick={() => toggleWatch(city.id)} title="Remove from watchlist"
                      style={{ position: 'absolute', top: 11, right: 11, background: 'none', border: 'none', cursor: 'pointer', padding: 2, lineHeight: 0 }}>
                      <Star size={16} color="#D97706" fill="#D97706" />
                    </button>
                    <button onClick={() => navigate(`/city/${city.id}`)} style={{ background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', width: '100%', padding: 0, fontFamily: 'inherit' }}>
                      <div style={{ fontWeight: 700, fontSize: 15, color: '#111827', fontFamily: 'DM Sans, sans-serif', paddingRight: 22 }}>{city.name}</div>
                      <div style={{ fontSize: 12, color: '#9CA3AF', margin: '2px 0 10px', fontWeight: 500 }}>{city.state}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ background: `${pc}10`, color: pc, border: `1px solid ${pc}20`, padding: '2px 9px', borderRadius: 100, fontSize: 10.5, fontWeight: 600, textTransform: 'capitalize' }}>{city.growth_phase}</span>
                        <span style={{ fontSize: 17, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: city.investment_score >= 70 ? '#059669' : city.investment_score >= 50 ? '#4338CA' : '#D97706' }}>{city.investment_score}</span>
                      </div>
                    </button>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}

        {/* ── Cities Near You (GPS) ── */}
        {geoStatus === 'ok' && nearby.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            style={{ marginBottom: 36 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
              <div style={{
                width: 32, height: 32, borderRadius: 9,
                background: 'rgba(5, 150, 105, 0.1)', border: '1px solid rgba(5, 150, 105, 0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Navigation size={15} color="#059669" strokeWidth={2.5} />
              </div>
              <span style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', letterSpacing: '-0.2px', fontFamily: 'DM Sans, sans-serif' }}>
                Cities Near You
              </span>
              {detectedRegion && (
                <span style={{
                  fontSize: 12.5, fontWeight: 600, color: '#059669',
                  background: 'rgba(5,150,105,0.08)', border: '1px solid rgba(5,150,105,0.2)',
                  borderRadius: 100, padding: '3px 11px',
                }}>
                  📍 You're near {detectedRegion}
                </span>
              )}
              <span style={{ marginLeft: 'auto', fontSize: 12, color: '#9CA3AF', fontWeight: 500 }}>
                based on your location · approximate
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 12 }}>
              {nearby.map((city, i) => {
                const tc = tierColor(city.tier)
                const pc = phaseColor(city.growth_phase)
                return (
                  <motion.button key={city.id}
                    custom={i} variants={fadeUp} initial="hidden" animate="visible"
                    whileHover={{ y: -4, boxShadow: '0 14px 40px rgba(0,0,0,0.1)' }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => navigate(`/city/${city.id}`)}
                    style={{
                      background: 'var(--bg-card)', border: '1px solid var(--border-faint)',
                      borderRadius: 16, padding: '15px 16px', textAlign: 'left', cursor: 'pointer',
                      boxShadow: 'var(--shadow-sm)', width: '100%', position: 'relative', overflow: 'hidden',
                    }}
                  >
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: `linear-gradient(90deg, ${tc}, ${pc})`, borderRadius: '16px 16px 0 0' }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, paddingTop: 5, marginBottom: 3 }}>
                      <span style={{ fontWeight: 700, fontSize: 15, color: '#111827', lineHeight: 1.2, fontFamily: 'DM Sans, sans-serif' }}>{city.name}</span>
                      <span style={{
                        fontSize: 11, fontWeight: 700, color: '#059669', whiteSpace: 'nowrap',
                        background: 'rgba(5,150,105,0.08)', border: '1px solid rgba(5,150,105,0.18)',
                        borderRadius: 100, padding: '2px 8px',
                      }}>{city.distance_km} km</span>
                    </div>
                    <div style={{ fontSize: 12, color: '#9CA3AF', marginBottom: 11, fontWeight: 500 }}>{city.state}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ background: `${pc}10`, color: pc, border: `1px solid ${pc}20`, padding: '2px 9px', borderRadius: 100, fontSize: 10.5, fontWeight: 600, textTransform: 'capitalize' }}>
                        {city.growth_phase}
                      </span>
                      <span style={{ fontSize: 17, fontWeight: 800, fontFamily: 'DM Sans, sans-serif', color: city.investment_score >= 70 ? '#059669' : city.investment_score >= 50 ? '#4338CA' : '#D97706' }}>
                        {city.investment_score}
                      </span>
                    </div>
                  </motion.button>
                )
              })}
            </div>
          </motion.div>
        )}

        {/* ── Map + Filters ── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          style={{ marginBottom: 36 }}
        >
          {/* Filter bar */}
          <div style={{
            display: 'flex', gap: 10, marginBottom: 14,
            alignItems: 'center', flexWrap: 'wrap',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-faint)',
            borderRadius: 14, padding: '10px 18px',
            boxShadow: 'var(--shadow-sm)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Cpu size={13} color="#9CA3AF" />
              <span style={{ fontSize: 11.5, color: '#9CA3AF', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                Filter
              </span>
            </div>
            <div style={{ width: 1, height: 18, background: 'var(--border)', margin: '0 4px' }} />

            <CustomSelect options={stateOptions} value={filterState} onChange={setFilterState} placeholder="All States" minWidth={140} />
            <CustomSelect options={tierOptions} value={filterTier} onChange={setFilterTier} placeholder="All Tiers" minWidth={132} />
            <CustomSelect options={phaseOptions} value={filterPhase} onChange={setFilterPhase} placeholder="All Phases" minWidth={132} />
            <CustomSelect options={priceOptions} value={maxPrice} onChange={setMaxPrice} placeholder="Any Budget" minWidth={140} />
            <div style={{ width: 1, height: 18, background: 'var(--border)', margin: '0 2px' }} />
            <CustomSelect options={sortOptions} value={sortBy} onChange={setSortBy} placeholder="Sort" minWidth={184} />

            {anyFilter && (
              <motion.button
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="btn btn-outline"
                style={{ padding: '6px 12px', fontSize: 12.5, height: 36 }}
                onClick={() => { setFilterState(''); setFilterTier(''); setFilterPhase(''); setMaxPrice('') }}
              >
                Clear
              </motion.button>
            )}
            {getAuthToken() && anyFilter && (
              <button
                className="btn btn-outline"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 12px', fontSize: 12.5, height: 36, color: savedSearch ? '#059669' : undefined }}
                title="Save these filters to your dashboard"
                onClick={async () => {
                  try {
                    await saveSearchApi('', { state: filterState, tier: filterTier, phase: filterPhase })
                    setSavedSearch(true); setTimeout(() => setSavedSearch(false), 1800)
                  } catch { /* ignore */ }
                }}
              >
                {savedSearch ? <><Check size={13} /> Saved</> : <><Bookmark size={13} /> Save search</>}
              </button>
            )}
            <span style={{ marginLeft: 'auto', fontSize: 12.5, color: '#9CA3AF', fontWeight: 500 }}>
              {filtered.length} cities
            </span>
          </div>

          <MapView cities={filtered} height={520} />
        </motion.div>

        {/* ── Distribution grid ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 36 }}>
          <motion.div
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.45 }}
          >
            <div className="section-title">Cities by Tier</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {tierCounts.map(({ tier, count }) => {
                const col = tierColor(tier)
                return (
                  <div key={tier} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                      width: 40, height: 40, borderRadius: 11, flexShrink: 0,
                      background: `${col}10`, border: `1px solid ${col}22`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <span style={{ fontWeight: 800, color: col, fontSize: 14 }}>{tier}</span>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7 }}>
                        <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', fontWeight: 500 }}>Tier {tier}</span>
                        <span style={{ fontSize: 13.5, fontWeight: 700, color: col }}>{count}</span>
                      </div>
                      <div className="progress-bar">
                        <motion.div
                          className="progress-fill"
                          initial={{ width: 0 }}
                          animate={{ width: `${cities.length ? (count / cities.length) * 100 : 0}%` }}
                          transition={{ delay: 0.4, duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
                          style={{ background: `linear-gradient(90deg, ${col}80, ${col})` }}
                        />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>

          <motion.div
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.45 }}
          >
            <div className="section-title">Cities by Growth Phase</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {phaseCounts.map(({ phase, count }) => {
                const col = phaseColor(phase)
                return (
                  <div key={phase} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                      width: 10, height: 10, borderRadius: '50%',
                      background: col, flexShrink: 0,
                      boxShadow: `0 0 8px ${col}60`,
                    }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7 }}>
                        <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', textTransform: 'capitalize', fontWeight: 500 }}>{phase}</span>
                        <span style={{ fontSize: 13.5, fontWeight: 700, color: col }}>{count}</span>
                      </div>
                      <div className="progress-bar">
                        <motion.div
                          className="progress-fill"
                          initial={{ width: 0 }}
                          animate={{ width: `${cities.length ? (count / cities.length) * 100 : 0}%` }}
                          transition={{ delay: 0.45, duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
                          style={{ background: `linear-gradient(90deg, ${col}80, ${col})` }}
                        />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        </div>

        {/* ── Spotlight: High-Potential Cities ── */}
        <div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            style={{
              display: 'flex', alignItems: 'center',
              justifyContent: 'space-between', marginBottom: 18,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 9,
                background: 'rgba(13, 148, 136, 0.1)',
                border: '1px solid rgba(13, 148, 136, 0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Zap size={15} color="#0D9488" strokeWidth={2.5} />
              </div>
              <span style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', letterSpacing: '-0.2px', fontFamily: 'DM Sans, sans-serif' }}>
                {gpsOn ? 'Top Opportunities Near You' : 'Top Investment Opportunities'}
              </span>
              {gpsOn && (
                <span style={{ fontSize: 12, fontWeight: 600, color: '#059669', background: 'rgba(5,150,105,0.08)', border: '1px solid rgba(5,150,105,0.2)', borderRadius: 100, padding: '3px 11px' }}>
                  📍 ranked by score near {detectedRegion || 'you'}
                </span>
              )}
            </div>
            <span style={{ fontSize: 12.5, color: '#9CA3AF', fontWeight: 500 }}>
              {topOpportunities.length} cities
            </span>
          </motion.div>

          <div className="grid-4" style={{ gap: 14 }}>
            {topOpportunities.map((city, i) => {
              const tc = tierColor(city.tier)
              const pc = phaseColor(city.growth_phase)
              const score = city.investment_score
              return (
                <motion.button key={city.id}
                  custom={i}
                  variants={fadeUp}
                  initial="hidden"
                  animate="visible"
                  whileHover={{ y: -5, boxShadow: '0 16px 48px rgba(0,0,0,0.1)' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigate(`/city/${city.id}`)}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-faint)',
                    borderRadius: 18,
                    padding: '18px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    position: 'relative', overflow: 'hidden',
                    boxShadow: 'var(--shadow-sm)',
                    width: '100%',
                    transition: 'border-color 0.2s',
                  }}
                >
                  {/* Colored top accent line */}
                  <div style={{
                    position: 'absolute', top: 0, left: 0, right: 0,
                    height: 3,
                    background: `linear-gradient(90deg, ${tc}, ${pc})`,
                    borderRadius: '18px 18px 0 0',
                  }} />

                  <div style={{ paddingTop: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 4 }}>
                      <div style={{ fontWeight: 700, fontSize: 15.5, color: '#111827', lineHeight: 1.2, fontFamily: 'DM Sans, sans-serif' }}>
                        {city.name}
                      </div>
                      <ArrowRight size={15} color="#9CA3AF" style={{ flexShrink: 0, marginTop: 2 }} />
                    </div>

                    <div style={{ fontSize: 12.5, color: '#9CA3AF', marginBottom: 12, fontWeight: 500 }}>
                      {city.state}
                    </div>

                    <div style={{ display: 'flex', gap: 5, marginBottom: 14, flexWrap: 'wrap' }}>
                      <span style={{
                        background: `${tc}10`, color: tc,
                        border: `1px solid ${tc}20`,
                        padding: '2px 9px', borderRadius: 100,
                        fontSize: 11, fontWeight: 600,
                      }}>Tier {city.tier}</span>
                      <span style={{
                        background: `${pc}10`, color: pc,
                        border: `1px solid ${pc}20`,
                        padding: '2px 9px', borderRadius: 100,
                        fontSize: 11, fontWeight: 600, textTransform: 'capitalize',
                      }}>{city.growth_phase}</span>
                    </div>

                    <div style={{
                      display: 'flex', justifyContent: 'space-between',
                      alignItems: 'flex-end',
                      paddingTop: 12,
                      borderTop: '1px solid var(--border-faint)',
                    }}>
                      <div>
                        <div style={{ fontSize: 10.5, color: '#9CA3AF', fontWeight: 500, marginBottom: 2 }}>Land Price</div>
                        <div style={{ fontSize: 13.5, fontWeight: 600, color: '#374151' }}>
                          ₹{city.land_price_inr_per_sqft['2021'].toLocaleString()}/sqft
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 10.5, color: '#9CA3AF', fontWeight: 500, marginBottom: 2 }}>Score</div>
                        <div style={{
                          fontSize: 22, fontWeight: 800, lineHeight: 1, fontFamily: 'DM Sans, sans-serif',
                          color: score >= 70 ? '#059669' : score >= 50 ? '#4338CA' : '#D97706',
                        }}>{score}</div>
                      </div>
                    </div>
                  </div>
                </motion.button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
