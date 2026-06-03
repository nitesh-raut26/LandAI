import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis, Cell,
} from 'recharts'
import { BarChart2, MapPin, TrendingUp, Layers, ArrowRight, Loader2 } from 'lucide-react'
import { fetchAllCities, tierColor, phaseColor, scoreColor } from '../utils/api'
import ProvenanceStrip from '../components/ProvenanceStrip'

const axisStyle = { fill: '#9CA3AF', fontSize: 11, fontWeight: 500 }
const gridStyle = { stroke: '#F3F4F6', strokeDasharray: '3 3' }

function Card({ title, icon: Icon, children, span }) {
  return (
    <div className="card" style={{ gridColumn: span ? `span ${span}` : undefined }}>
      <div className="section-title">{Icon && <Icon size={13} />}{title}</div>
      {children}
    </div>
  )
}

const Tip = ({ active, payload, label, fmt }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#fff', border: '1.5px solid rgba(17,24,39,0.1)', borderRadius: 10, padding: '10px 13px', fontSize: 12.5, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
      <div style={{ fontWeight: 700, color: '#111827', marginBottom: 4 }}>{payload[0]?.payload?.name || label}</div>
      {payload.map((p, i) => <div key={i} style={{ color: '#6B7280' }}>{fmt ? fmt(p) : `${p.name}: ${p.value}`}</div>)}
    </div>
  )
}

export default function Analytics() {
  const [cities, setCities] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchAllCities().then(c => { setCities(Array.isArray(c) ? c : []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const stats = useMemo(() => {
    if (!cities.length) return null
    const avg = (f) => Math.round(cities.reduce((s, c) => s + f(c), 0) / cities.length)
    const byState = {}
    cities.forEach(c => { (byState[c.state] ??= []).push(c) })
    const stateRows = Object.entries(byState)
      .map(([state, list]) => ({ name: state, count: list.length, score: Math.round(list.reduce((s, c) => s + c.investment_score, 0) / list.length) }))
      .sort((a, b) => b.score - a.score).slice(0, 12)
    const tierRows = [1, 2, 3].map(t => ({ name: `Tier ${t}`, value: cities.filter(c => c.tier === t).length, color: tierColor(t) }))
    const phaseRows = ['emerging', 'accelerating', 'maturing', 'mature'].map(p => ({ name: p[0].toUpperCase() + p.slice(1), value: cities.filter(c => c.growth_phase === p).length, color: phaseColor(p) }))
    const scatter = cities.map(c => ({ name: c.name, x: c.land_price_inr_per_sqft['2021'], y: c.investment_score, tier: c.tier, id: c.id }))
    const top = [...cities].sort((a, b) => b.investment_score - a.investment_score).slice(0, 8)
    return { avgScore: avg(c => c.investment_score), stateRows, tierRows, phaseRows, scatter, top, states: Object.keys(byState).length }
  }, [cities])

  if (loading || !stats) return (
    <div style={{ minHeight: '70vh', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, color: '#9CA3AF' }}>
      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 0.9, ease: 'linear' }}><Loader2 size={26} color="var(--teal)" /></motion.div>
      Loading analytics…
    </div>
  )

  const TILES = [
    { label: 'Cities Tracked', value: cities.length, icon: MapPin, color: '#4338CA' },
    { label: 'States & UTs', value: stats.states, icon: Layers, color: '#0D9488' },
    { label: 'Avg Investment Score', value: stats.avgScore, icon: BarChart2, color: '#D97706' },
    { label: 'Emerging Markets', value: cities.filter(c => c.growth_phase === 'emerging').length, icon: TrendingUp, color: '#059669' },
  ]

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh' }}>
      <div style={{ maxWidth: 1340, margin: '0 auto', padding: '32px 24px 64px' }}>
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 24 }}>
          <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.6px', color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>Market Analytics</h1>
          <p style={{ fontSize: 14.5, color: '#6B7280', marginTop: 6 }}>Cross-market intelligence across {cities.length} cities and {stats.states} states & UTs.</p>
          <div style={{ marginTop: 14 }}>
            <ProvenanceStrip kind="curated" provenance={{ source: 'Curated 116-city database', license: 'internal' }}
              note="Distributions are computed from the curated, census-aligned city database — directional, not live market transactions. Investment scores are heuristic." />
          </div>
        </motion.div>

        {/* tiles */}
        <div className="grid-4" style={{ marginBottom: 16 }}>
          {TILES.map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ width: 46, height: 46, borderRadius: 13, background: `${color}12`, border: `1px solid ${color}25`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon size={20} color={color} strokeWidth={2} />
              </div>
              <div>
                <div style={{ fontSize: 26, fontWeight: 800, color, lineHeight: 1, fontFamily: 'DM Sans, sans-serif' }}>{value}</div>
                <div style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4, fontWeight: 500 }}>{label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* state bar */}
        <div style={{ marginBottom: 16 }}>
          <Card title="Top States by Average Investment Score" icon={MapPin}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.stateRows} margin={{ top: 4, right: 12, bottom: 40, left: 0 }}>
                <CartesianGrid {...gridStyle} vertical={false} />
                <XAxis dataKey="name" tick={axisStyle} axisLine={false} tickLine={false} angle={-35} textAnchor="end" interval={0} height={60} />
                <YAxis tick={axisStyle} axisLine={false} tickLine={false} domain={[0, 100]} width={36} />
                <Tooltip content={<Tip fmt={p => `Avg score: ${p.value} · ${p.payload.count} cities`} />} cursor={{ fill: 'rgba(67,56,202,0.05)' }} />
                <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                  {stats.stateRows.map((r, i) => <Cell key={i} fill={scoreColor(r.score)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* tier + phase */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }} className="an-2col">
          <style>{`@media(max-width:760px){.an-2col{grid-template-columns:1fr!important}}`}</style>
          <Card title="Cities by Tier" icon={Layers}>
            <ResponsiveContainer width="100%" height={230}>
              <BarChart data={stats.tierRows} margin={{ top: 4, right: 12, bottom: 0, left: 0 }}>
                <CartesianGrid {...gridStyle} vertical={false} />
                <XAxis dataKey="name" tick={axisStyle} axisLine={false} tickLine={false} />
                <YAxis tick={axisStyle} axisLine={false} tickLine={false} width={32} />
                <Tooltip content={<Tip fmt={p => `${p.value} cities`} />} cursor={{ fill: 'rgba(0,0,0,0.03)' }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>{stats.tierRows.map((r, i) => <Cell key={i} fill={r.color} />)}</Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
          <Card title="Cities by Growth Phase" icon={TrendingUp}>
            <ResponsiveContainer width="100%" height={230}>
              <BarChart data={stats.phaseRows} margin={{ top: 4, right: 12, bottom: 0, left: 0 }}>
                <CartesianGrid {...gridStyle} vertical={false} />
                <XAxis dataKey="name" tick={axisStyle} axisLine={false} tickLine={false} />
                <YAxis tick={axisStyle} axisLine={false} tickLine={false} width={32} />
                <Tooltip content={<Tip fmt={p => `${p.value} cities`} />} cursor={{ fill: 'rgba(0,0,0,0.03)' }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>{stats.phaseRows.map((r, i) => <Cell key={i} fill={r.color} />)}</Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* scatter */}
        <div style={{ marginBottom: 16 }}>
          <Card title="Land Price vs Investment Score (each dot = a city)" icon={BarChart2}>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart margin={{ top: 8, right: 16, bottom: 16, left: 4 }}>
                <CartesianGrid {...gridStyle} />
                <XAxis type="number" dataKey="x" name="Price" tick={axisStyle} axisLine={false} tickLine={false}
                  tickFormatter={v => v >= 1000 ? `₹${(v / 1000).toFixed(0)}k` : `₹${v}`} />
                <YAxis type="number" dataKey="y" name="Score" tick={axisStyle} axisLine={false} tickLine={false} domain={[0, 100]} width={32} />
                <ZAxis range={[40, 40]} />
                <Tooltip content={<Tip fmt={p => p.name === 'Price' ? `₹${p.value.toLocaleString()}/sqft` : `Score: ${p.value}`} />} cursor={{ strokeDasharray: '3 3' }} />
                <Scatter data={stats.scatter} onClick={(d) => d?.id && navigate(`/city/${d.id}`)} cursor="pointer">
                  {stats.scatter.map((d, i) => <Cell key={i} fill={tierColor(d.tier)} fillOpacity={0.7} />)}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
            <div style={{ display: 'flex', gap: 16, marginTop: 8, justifyContent: 'center' }}>
              {[1, 2, 3].map(t => (
                <span key={t} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#6B7280' }}>
                  <span style={{ width: 9, height: 9, borderRadius: '50%', background: tierColor(t) }} /> Tier {t}
                </span>
              ))}
            </div>
          </Card>
        </div>

        {/* top opportunities */}
        <Card title="Top Investment Opportunities" icon={TrendingUp}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
            {stats.top.map(c => (
              <motion.button key={c.id} whileHover={{ y: -3, boxShadow: '0 10px 28px rgba(0,0,0,0.08)' }}
                onClick={() => navigate(`/city/${c.id}`)}
                style={{ textAlign: 'left', background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 13, padding: '13px 14px', cursor: 'pointer', fontFamily: 'inherit' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: 14.5, color: '#111827', fontFamily: 'DM Sans, sans-serif' }}>{c.name}</span>
                  <span style={{ fontSize: 16, fontWeight: 800, color: scoreColor(c.investment_score), fontFamily: 'DM Sans, sans-serif' }}>{c.investment_score}</span>
                </div>
                <div style={{ fontSize: 12, color: '#9CA3AF', margin: '3px 0 8px', fontWeight: 500 }}>{c.state} · Tier {c.tier}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 11, fontWeight: 600, color: phaseColor(c.growth_phase), background: `${phaseColor(c.growth_phase)}12`, border: `1px solid ${phaseColor(c.growth_phase)}25`, padding: '2px 9px', borderRadius: 100, textTransform: 'capitalize' }}>{c.growth_phase}</span>
                  <ArrowRight size={14} color="#9CA3AF" />
                </div>
              </motion.button>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
