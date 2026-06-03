import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { UserCircle2, Hammer, Globe2, Scale } from 'lucide-react'
import { fetchScore, fetchPersonas, scoreColor } from '../utils/api'
import ProvenanceStrip from './ProvenanceStrip'

const PERSONA_ICON = { balanced: Scale, small: UserCircle2, builder: Hammer, nri: Globe2 }
const REC_COLOR = {
  'Buy Now': '#059669', 'Buy Early': '#4338CA', 'Watch': '#D97706', 'Hold': '#6B7280',
}

/**
 * Investor Persona Mode (Vision §3.5): a toggle that re-weights the SAME
 * transparent sub-scores for a Small Investor / Builder / NRI / Balanced buyer,
 * and shows how the composite shifts across personas.
 */
export default function PersonaScore({ cityId }) {
  const [personas, setPersonas] = useState([])
  const [persona, setPersona] = useState('balanced')
  const [data, setData] = useState(null)

  useEffect(() => { fetchPersonas().then(r => setPersonas(r.personas || [])).catch(() => {}) }, [])
  useEffect(() => {
    if (!cityId) return
    fetchScore(cityId, persona).then(setData).catch(() => setData(null))
  }, [cityId, persona])

  if (!data) return null
  const composite = data.composite_score
  const sc = scoreColor(composite)
  const recColor = REC_COLOR[data.recommendation] || '#6B7280'
  const spread = data.persona_scores || {}

  return (
    <div className="card">
      <div className="section-title"><UserCircle2 size={13} /> Investor Persona Lens</div>

      {/* Persona toggle */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 16 }}>
        {(personas.length ? personas : [{ key: 'balanced', label: 'Balanced' }]).map(p => {
          const Icon = PERSONA_ICON[p.key] || Scale
          const active = persona === p.key
          return (
            <button key={p.key} onClick={() => setPersona(p.key)}
              title={p.focus}
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 6, cursor: 'pointer',
                fontSize: 12.5, fontWeight: 600, fontFamily: 'inherit',
                padding: '6px 12px', borderRadius: 100, transition: 'all 0.18s',
                background: active ? 'linear-gradient(135deg, #4338CA, #0D9488)' : 'var(--bg-base)',
                color: active ? '#fff' : '#6B7280',
                border: `1px solid ${active ? 'transparent' : 'var(--border-faint)'}`,
                boxShadow: active ? '0 2px 12px rgba(67,56,202,0.25)' : 'none',
              }}>
              <Icon size={13} /> {p.label?.replace(' / Developer', '').replace(' Investor', '')}
            </button>
          )
        })}
      </div>

      {/* Persona composite + recommendation */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 14 }}>
        <div style={{
          width: 76, height: 76, borderRadius: '50%', flexShrink: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: `conic-gradient(${sc} ${composite * 3.6}deg, #F3F4F6 0deg)`,
        }}>
          <div style={{
            width: 60, height: 60, borderRadius: '50%', background: 'var(--bg-card)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          }}>
            <span style={{ fontSize: 22, fontWeight: 800, color: sc, fontFamily: 'DM Sans, sans-serif', lineHeight: 1 }}>{composite}</span>
            <span style={{ fontSize: 9.5, color: '#9CA3AF' }}>/ 100</span>
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 8,
            background: `${recColor}12`, border: `1px solid ${recColor}30`,
            borderRadius: 9, padding: '5px 12px',
          }}>
            <span style={{ fontWeight: 700, fontSize: 14, color: recColor, fontFamily: 'DM Sans, sans-serif' }}>{data.recommendation}</span>
          </div>
          <div style={{ fontSize: 12.5, color: '#6B7280', lineHeight: 1.55 }}>{data.persona_fit}</div>
        </div>
      </div>

      {/* Cross-persona spread */}
      <div style={{ background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 12, padding: '12px 14px', marginBottom: 12 }}>
        <div style={{ fontSize: 10.5, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600, marginBottom: 9 }}>
          Composite by persona
        </div>
        {Object.entries(spread).map(([key, val]) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 7 }}>
            <span style={{ fontSize: 11.5, color: key === persona ? 'var(--text-primary)' : '#9CA3AF', fontWeight: key === persona ? 700 : 500, width: 64, textTransform: 'capitalize' }}>{key}</span>
            <div style={{ flex: 1, height: 6, background: '#F3F4F6', borderRadius: 100, overflow: 'hidden' }}>
              <motion.div initial={{ width: 0 }} animate={{ width: `${val}%` }} transition={{ duration: 0.5 }}
                style={{ height: '100%', background: scoreColor(val), borderRadius: 100 }} />
            </div>
            <span style={{ fontSize: 11.5, fontWeight: 700, color: scoreColor(val), width: 30, textAlign: 'right' }}>{val}</span>
          </div>
        ))}
      </div>

      <ProvenanceStrip kind="heuristic" provenance={{ source: 'Persona-weighted scoring' }}
        note="Same transparent sub-scores, re-weighted per investor persona. Directional, not investment advice." />
    </div>
  )
}
