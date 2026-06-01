import { motion } from 'framer-motion'
import { TrendingUp, Shield, Zap, BarChart2 } from 'lucide-react'
import { scoreColor, phaseColor } from '../utils/api'

function ScoreBar({ label, score, color }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 13, color: '#6B7280', fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: 13, fontWeight: 700, color }}>{Math.round(score)}</span>
      </div>
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ delay: 0.3, duration: 0.85, ease: [0.4, 0, 0.2, 1] }}
          style={{ background: `linear-gradient(90deg, ${color}70, ${color})` }}
        />
      </div>
    </div>
  )
}

function Ring({ score }) {
  const color = scoreColor(score)
  const r      = 44
  const circ   = 2 * Math.PI * r
  const dash   = (score / 100) * circ
  return (
    <svg width={110} height={110} viewBox="0 0 110 110" style={{ flexShrink: 0 }}>
      {/* Track */}
      <circle cx={55} cy={55} r={r} fill="none" stroke="#F3F4F6" strokeWidth={9} />
      {/* Filled arc */}
      <motion.circle
        cx={55} cy={55} r={r} fill="none" stroke={color} strokeWidth={9}
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        transform="rotate(-90 55 55)"
        initial={{ strokeDasharray: `0 ${circ}` }}
        animate={{ strokeDasharray: `${dash} ${circ}` }}
        transition={{ delay: 0.2, duration: 0.9, ease: [0.4, 0, 0.2, 1] }}
        style={{ filter: `drop-shadow(0 0 6px ${color}60)` }}
      />
      <text x={55} y={50} textAnchor="middle" dominantBaseline="middle"
        fill={color} fontSize={23} fontWeight={800} fontFamily="DM Sans, sans-serif">{Math.round(score)}</text>
      <text x={55} y={68} textAnchor="middle" dominantBaseline="middle"
        fill="#9CA3AF" fontSize={10}>/ 100</text>
    </svg>
  )
}

const RECS = {
  'Buy Now':  { color: '#059669', bg: 'rgba(5,150,105,0.08)',   border: 'rgba(5,150,105,0.2)',   icon: TrendingUp },
  'Buy Early':{ color: '#4338CA', bg: 'rgba(67,56,202,0.08)',   border: 'rgba(67,56,202,0.2)',   icon: Zap        },
  'Watch':    { color: '#D97706', bg: 'rgba(245,158,11,0.08)',  border: 'rgba(245,158,11,0.2)',  icon: Shield     },
  'Hold':     { color: '#6B7280', bg: 'rgba(107,114,128,0.07)', border: 'rgba(107,114,128,0.16)', icon: BarChart2  },
}

const REC_TEXT = {
  'Buy Now':   'High growth probability. Early-stage city with strong fundamentals.',
  'Buy Early': 'Accelerating growth phase. Good entry before prices peak.',
  'Watch':     'Steady growth. Monitor for infrastructure triggers.',
  'Hold':      'Mature market. Stable appreciation, limited upside.',
}

function getRec(score, phase) {
  if (phase === 'emerging'     && score >= 65) return 'Buy Now'
  if (phase === 'accelerating' && score >= 60) return 'Buy Early'
  if (phase === 'maturing')  return 'Watch'
  if (phase === 'mature')    return 'Hold'
  return score >= 70 ? 'Buy Early' : 'Watch'
}

export default function InvestmentScore({ city, prediction }) {
  if (!city) return null

  const score  = city.investment_score
  const phase  = city.growth_phase
  const rec    = getRec(score, phase)
  const meta   = RECS[rec] || RECS['Watch']
  const Icon   = meta.icon
  const sc     = scoreColor(score)

  const cagr   = prediction?.annual_cagr_price_pct || 0
  const rise5  = prediction?.milestones?.price_appreciation_5yr_pct  || 0
  const rise10 = prediction?.milestones?.price_appreciation_10yr_pct || 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Score ring + recommendation */}
      <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
        <Ring score={score} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 10.5, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: 7, fontWeight: 600 }}>
            Investment Signal
          </div>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 9,
            background: meta.bg, border: `1px solid ${meta.border}`,
            borderRadius: 10, padding: '7px 14px',
          }}>
            <Icon size={14} color={meta.color} />
            <span style={{ fontWeight: 700, fontSize: 15, color: meta.color, fontFamily: 'DM Sans, sans-serif' }}>{rec}</span>
          </div>
          <div style={{ fontSize: 13, color: '#6B7280', lineHeight: 1.6 }}>
            {REC_TEXT[rec]}
          </div>
        </div>
      </div>

      {/* Score breakdown */}
      <div style={{
        background: 'var(--bg-base)',
        border: '1px solid var(--border-faint)',
        borderRadius: 13, padding: '15px 17px',
      }}>
        <div className="section-title" style={{ marginBottom: 14 }}>Score Breakdown</div>
        <ScoreBar label="Infrastructure Quality" score={city.scores.infrastructure}    color="#4338CA" />
        <ScoreBar label="Connectivity Index"      score={city.scores.connectivity}      color="#0D9488" />
        <ScoreBar label="Economic Activity"        score={city.scores.economic_activity} color="#D97706" />
        <ScoreBar label="Overall Composite"        score={city.scores.overall}           color={sc}      />
      </div>

      {/* Price forecast */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
        {[
          { label: 'Annual CAGR',  value: `${cagr}%`,    color: '#4338CA' },
          { label: '5-Year Rise',  value: `+${rise5}%`,  color: '#059669' },
          { label: '10-Year Rise', value: `+${rise10}%`, color: '#D97706' },
        ].map(item => (
          <motion.div key={item.label}
            whileHover={{ y: -2 }}
            style={{
              background: 'var(--bg-base)',
              border: '1px solid var(--border-faint)',
              borderRadius: 11, padding: '12px 10px', textAlign: 'center',
            }}>
            <div style={{ fontSize: 10.5, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4, fontWeight: 500 }}>
              {item.label}
            </div>
            <div style={{ fontSize: 20, fontWeight: 800, color: item.color, letterSpacing: '-0.3px', fontFamily: 'DM Sans, sans-serif' }}>
              {item.value}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Growth phase indicator */}
      <div style={{
        background: `${phaseColor(phase)}06`,
        border: `1px solid ${phaseColor(phase)}18`,
        borderRadius: 13, padding: '13px 15px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <span style={{ fontSize: 12.5, color: '#9CA3AF', fontWeight: 500 }}>Growth Phase</span>
          <span style={{ fontWeight: 700, fontSize: 13.5, color: phaseColor(phase), textTransform: 'capitalize' }}>
            {phase}
          </span>
        </div>
        <div style={{ display: 'flex', gap: 5 }}>
          {['emerging', 'accelerating', 'maturing', 'mature'].map(p => (
            <motion.div key={p}
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ delay: 0.4, duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
              style={{
                flex: 1, height: 5, borderRadius: 100,
                background: p === phase ? phaseColor(p) : '#F3F4F6',
                opacity: p === phase ? 1 : 0.5,
                boxShadow: p === phase ? `0 0 8px ${phaseColor(p)}50` : 'none',
              }}
            />
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
          {['Emerging', 'Growing', 'Maturing', 'Mature'].map(l => (
            <span key={l} style={{ fontSize: 9.5, color: '#9CA3AF', fontWeight: 500 }}>{l}</span>
          ))}
        </div>
      </div>

      {/* Growth triggers */}
      {city.growth_triggers?.length > 0 && (
        <div>
          <div className="section-title" style={{ marginBottom: 9 }}>Growth Triggers</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
            {city.growth_triggers.map(trigger => (
              <span key={trigger} className="tag" style={{ fontSize: 11.5 }}>
                {trigger.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
