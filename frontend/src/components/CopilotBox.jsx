import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, ArrowRight, Loader2, CornerDownLeft } from 'lucide-react'
import { runCopilot, scoreColor } from '../utils/api'
import ProvenanceStrip from './ProvenanceStrip'

const EXAMPLES = [
  'Best city under ₹20 lakh near a metro',
  'Low-risk Tier-2 cities in Gujarat',
  'Highest ROI emerging towns',
  'Alternatives to Bangalore',
]

const RISK_COLOR = { low: '#059669', medium: '#D97706', high: '#F43F5E' }

export default function CopilotBox() {
  const [q, setQ] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const ask = (query) => {
    const text = (query ?? q).trim()
    if (!text) return
    setQ(text); setLoading(true)
    runCopilot(text, 6).then(r => { setData(r); setLoading(false) }).catch(() => setLoading(false))
  }

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(67,56,202,0.05), rgba(13,148,136,0.05))',
      border: '1px solid rgba(67,56,202,0.16)', borderRadius: 20, padding: '22px 22px 24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div style={{
          width: 34, height: 34, borderRadius: 10, flexShrink: 0,
          background: 'linear-gradient(135deg, #4338CA, #0D9488)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 14px rgba(67,56,202,0.3)',
        }}>
          <Sparkles size={17} color="#fff" />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif', lineHeight: 1.1 }}>
            AI Investment Copilot
          </div>
          <div style={{ fontSize: 12.5, color: '#9CA3AF', marginTop: 2 }}>Ask in plain English — it understands budget, risk, ROI, metros & more</div>
        </div>
      </div>

      {/* input */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: 240 }}>
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') ask() }}
            placeholder="e.g. cheap high-growth cities near a metro under ₹2000/sqft"
            style={{ paddingRight: 40 }}
          />
          <CornerDownLeft size={15} color="#C7CBD1" style={{ position: 'absolute', right: 13, top: '50%', transform: 'translateY(-50%)' }} />
        </div>
        <motion.button whileTap={{ scale: 0.97 }} className="btn btn-primary" onClick={() => ask()} style={{ height: 44, paddingInline: 20 }}>
          {loading ? <Loader2 size={15} className="spin" style={{ animation: 'spin 0.9s linear infinite' }} /> : <Sparkles size={15} />}
          Ask
        </motion.button>
      </div>

      {/* examples */}
      <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap', marginTop: 12 }}>
        {EXAMPLES.map(ex => (
          <button key={ex} onClick={() => ask(ex)}
            style={{
              fontSize: 12, color: 'var(--indigo)', background: 'rgba(67,56,202,0.06)',
              border: '1px solid rgba(67,56,202,0.16)', borderRadius: 100, padding: '5px 12px',
              cursor: 'pointer', fontFamily: 'inherit',
            }}>
            {ex}
          </button>
        ))}
      </div>

      {/* results */}
      <AnimatePresence>
        {data && (
          <motion.div
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
            style={{ overflow: 'hidden' }}
          >
            <div style={{ marginTop: 18, paddingTop: 16, borderTop: '1px solid var(--border-faint)' }}>
              <div style={{ fontSize: 13.5, color: 'var(--text-secondary)', fontWeight: 500, marginBottom: 12 }}>
                {data.summary}
              </div>
              {data.results.length === 0 ? (
                <div style={{ fontSize: 13, color: '#9CA3AF', padding: '8px 0' }}>No cities matched — try widening the budget or removing a filter.</div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
                  {data.results.map((r, i) => (
                    <motion.button key={r.city_id}
                      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
                      whileHover={{ y: -3, boxShadow: '0 10px 28px rgba(0,0,0,0.08)' }}
                      onClick={() => navigate(`/city/${r.city_id}`)}
                      style={{
                        textAlign: 'left', background: 'var(--bg-card)', border: '1px solid var(--border-faint)',
                        borderRadius: 13, padding: '13px 14px', cursor: 'pointer', fontFamily: 'inherit',
                      }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                        <span style={{ fontWeight: 700, fontSize: 14.5, color: '#111827', fontFamily: 'DM Sans, sans-serif' }}>{r.name}</span>
                        <span style={{ fontSize: 16, fontWeight: 800, color: scoreColor(r.investment_score), fontFamily: 'DM Sans, sans-serif' }}>{r.investment_score}</span>
                      </div>
                      <div style={{ fontSize: 12, color: '#9CA3AF', margin: '2px 0 9px', fontWeight: 500 }}>{r.state} · Tier {r.tier}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8, flexWrap: 'wrap' }}>
                        <span style={{ fontSize: 11, fontWeight: 600, color: RISK_COLOR[r.risk_level], background: `${RISK_COLOR[r.risk_level]}14`, border: `1px solid ${RISK_COLOR[r.risk_level]}30`, padding: '1px 8px', borderRadius: 100 }}>{r.risk_level} risk</span>
                        <span style={{ fontSize: 11, fontWeight: 600, color: '#0D9488', background: 'rgba(13,148,136,0.08)', border: '1px solid rgba(13,148,136,0.18)', padding: '1px 8px', borderRadius: 100 }}>ROI {r.roi_score}</span>
                      </div>
                      <div style={{ fontSize: 11.5, color: '#6B7280', display: 'flex', alignItems: 'center', gap: 4 }}>
                        {r.reason} <ArrowRight size={11} style={{ marginLeft: 'auto', flexShrink: 0 }} color="#9CA3AF" />
                      </div>
                    </motion.button>
                  ))}
                </div>
              )}
              <div style={{ marginTop: 14 }}>
                <ProvenanceStrip kind="heuristic" provenance={{ source: 'Rule-based NLU over the city database' }}
                  note="Ranked by a deterministic keyword/regex parser over the curated database — NOT an LLM. Results are explainable and reproducible." />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
