import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Cpu, Activity, Satellite, Loader2, TrendingUp, Building2, Train, Plane, Factory, Home as HomeIcon, Radio, Gauge, ThumbsUp, AlertTriangle } from 'lucide-react'
import { fetchMlPrice, fetchSignals, fetchCvMetrics, fetchScore, cvRasterUrl, scoreColor } from '../utils/api'
import ProvenanceStrip from './ProvenanceStrip'

const PROJECT_LABEL = {
  airport: 'Airport', metro_rail: 'Metro Rail', industrial_corridor: 'Industrial Corridor',
  expressway: 'Expressway / Highway', railway: 'Railway', smart_city: 'Smart City',
  realty: 'Real Estate', other: 'Other',
}
const PROJECT_ICON = {
  airport: Plane, metro_rail: Train, industrial_corridor: Factory, expressway: TrendingUp,
  railway: Train, smart_city: Building2, realty: HomeIcon, other: Radio,
}
const STATUS_COLOR = {
  operational: '#059669', under_construction: '#0D9488', approved: '#4338CA',
  tendering: '#D97706', proposed: '#6B7280',
}
const fmtPrice = (v) => `₹${Number(v).toLocaleString()}`
const pretty = (s) => (s || '').replace(/_/g, ' ')

function Backend({ value }) {
  const mock = value === 'mock-fallback'
  return (
    <span style={{
      fontSize: 10.5, fontWeight: 700, letterSpacing: '0.4px', textTransform: 'uppercase',
      padding: '2px 8px', borderRadius: 100,
      background: mock ? 'rgba(245,158,11,0.1)' : 'rgba(5,150,105,0.1)',
      color: mock ? '#D97706' : '#059669',
      border: `1px solid ${mock ? 'rgba(245,158,11,0.25)' : 'rgba(5,150,105,0.25)'}`,
    }}>{mock ? 'offline mock' : value}</span>
  )
}

function Panel({ icon: Icon, title, accent, badge, children }) {
  return (
    <div style={{ background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 14, padding: '16px 18px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 14 }}>
        <div style={{
          width: 30, height: 30, borderRadius: 9, flexShrink: 0,
          background: `${accent}12`, border: `1px solid ${accent}28`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Icon size={15} color={accent} strokeWidth={2.2} />
        </div>
        <span style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>{title}</span>
        <span style={{ marginLeft: 'auto' }}>{badge}</span>
      </div>
      {children}
    </div>
  )
}

export default function AiIntelligence({ cityId }) {
  const [ml, setMl] = useState(null)
  const [sig, setSig] = useState(null)
  const [cv, setCv] = useState(null)
  const [score, setScore] = useState(null)
  const [loading, setLoading] = useState(true)
  const [imgOk, setImgOk] = useState(true)

  useEffect(() => {
    if (!cityId) return
    setLoading(true); setImgOk(true)
    Promise.all([fetchMlPrice(cityId, 10), fetchSignals(cityId, 6), fetchCvMetrics(cityId), fetchScore(cityId)])
      .then(([m, s, c, sc]) => { setMl(m); setSig(s); setCv(c); setScore(sc) })
      .finally(() => setLoading(false))
  }, [cityId])

  if (loading) return (
    <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, color: '#9CA3AF' }}>
      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 0.9, ease: 'linear' }}>
        <Loader2 size={22} color="var(--teal)" />
      </motion.div>
      Running AI models…
    </div>
  )

  const contribs = ml?.top_feature_contributions || []
  const maxAbs = Math.max(0.0001, ...contribs.map(c => Math.abs(c.contribution)))
  const cov = ml?.predicted_cagr_interval_pct?.nominal_coverage
  const mlNote = `${cov ? Math.round(cov * 100) + '% conformal interval · ' : ''}trained on 116 curated rows (leakage-audited; CV R² ≈ 0.21). Directional, not investment advice.`

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* ── Investment rationale / scoring ── */}
      {score && (
        <Panel icon={Gauge} title="Investment Rationale" accent="#D97706"
          badge={<span style={{ fontSize: 12, color: '#6B7280', fontWeight: 600 }}>
            composite <strong style={{ color: scoreColor(score.composite_score) }}>{score.composite_score}</strong> · {score.recommendation}
          </span>}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 14 }}>
            {[
              ['ROI potential', score.sub_scores.roi_score, '#059669'],
              ['Demand', score.sub_scores.demand_score, '#0D9488'],
              ['Future development', score.sub_scores.future_development_probability, '#4338CA'],
              ['Liquidity', score.sub_scores.liquidity_score, '#6366F1'],
              ['Risk', score.sub_scores.risk_score, score.sub_scores.risk_level === 'high' ? '#F43F5E' : score.sub_scores.risk_level === 'medium' ? '#D97706' : '#059669'],
            ].map(([label, val, col]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: 12, color: '#6B7280', width: 130, flexShrink: 0, fontWeight: 500 }}>{label}{label === 'Risk' ? ` (${score.sub_scores.risk_level})` : ''}</span>
                <div className="progress-bar" style={{ flex: 1 }}>
                  <div className="progress-fill" style={{ width: `${val}%`, background: `linear-gradient(90deg, ${col}80, ${col})` }} />
                </div>
                <span style={{ fontSize: 12, fontWeight: 700, color: col, width: 32, textAlign: 'right' }}>{Math.round(val)}</span>
              </div>
            ))}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11.5, fontWeight: 700, color: '#059669', marginBottom: 7, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                <ThumbsUp size={13} /> Strengths
              </div>
              {score.rationale.strengths.map((s, i) => (
                <div key={i} style={{ fontSize: 12.5, color: '#6B7280', lineHeight: 1.5, marginBottom: 5, paddingLeft: 12, position: 'relative' }}>
                  <span style={{ position: 'absolute', left: 0, color: '#059669' }}>•</span>{s}
                </div>
              ))}
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11.5, fontWeight: 700, color: '#D97706', marginBottom: 7, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                <AlertTriangle size={13} /> Watch-outs
              </div>
              {score.rationale.watch_outs.map((s, i) => (
                <div key={i} style={{ fontSize: 12.5, color: '#6B7280', lineHeight: 1.5, marginBottom: 5, paddingLeft: 12, position: 'relative' }}>
                  <span style={{ position: 'absolute', left: 0, color: '#D97706' }}>•</span>{s}
                </div>
              ))}
            </div>
          </div>
          <div style={{ marginTop: 14 }}>
            <ProvenanceStrip kind="heuristic" provenance={{ source: 'Weighted scoring formulas' }} note="Heuristic weighted sub-scores (ROI / risk / liquidity / demand) + real XGBoost SHAP drivers — not a learned ranking model." />
          </div>
        </Panel>
      )}

      {/* ── XGBoost price model ── */}
      <Panel icon={Cpu} title="Land-Price Model (XGBoost)" accent="#4338CA" badge={<Backend value={ml?.model_backend} />}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 14 }}>
          {[
            { label: 'Predicted CAGR', value: `${ml?.predicted_annual_cagr_pct ?? '—'}%`, color: '#4338CA' },
            { label: 'Price in 5 yrs', value: ml ? fmtPrice(ml.projected_price_5yr) : '—', color: '#0D9488' },
            { label: 'Price in 10 yrs', value: ml ? fmtPrice(ml.projected_price_10yr) : '—', color: '#059669' },
          ].map(s => (
            <div key={s.label} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 12px', textAlign: 'center' }}>
              <div className="stat-label" style={{ marginBottom: 4 }}>{s.label}</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: s.color, fontFamily: 'DM Sans, sans-serif', letterSpacing: '-0.3px' }}>{s.value}</div>
            </div>
          ))}
        </div>
        {contribs.length > 0 && (
          <>
            <div className="section-title" style={{ marginBottom: 10 }}>Top Feature Contributions (TreeSHAP)</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {contribs.map(c => {
                const pos = c.contribution >= 0
                const w = (Math.abs(c.contribution) / maxAbs) * 50
                return (
                  <div key={c.feature} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 11.5, color: '#6B7280', width: 150, flexShrink: 0, fontWeight: 500 }}>{pretty(c.feature)}</span>
                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', height: 14 }}>
                      <div style={{ width: '50%', display: 'flex', justifyContent: 'flex-end' }}>
                        {!pos && <div style={{ width: `${w}%`, height: 9, background: '#F43F5E', borderRadius: 3 }} />}
                      </div>
                      <div style={{ width: 1, height: 14, background: 'var(--border)' }} />
                      <div style={{ width: '50%' }}>
                        {pos && <div style={{ width: `${w}%`, height: 9, background: '#059669', borderRadius: 3 }} />}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
            <div style={{ fontSize: 11, color: '#9CA3AF', marginTop: 8 }}>
              Green = pushes growth up · Red = pushes down. Model target: historical land-price CAGR.
            </div>
          </>
        )}
        <div style={{ marginTop: 14 }}>
          <ProvenanceStrip kind="model" provenance={{ source: 'XGBoost land-price model' }} note={mlNote} />
        </div>
      </Panel>

      {/* ── NLP infrastructure signals ── */}
      <Panel icon={Activity} title="Infrastructure Signals (NLP)" accent="#0D9488"
        badge={sig && <span style={{ fontSize: 12, color: '#6B7280', fontWeight: 600 }}>
          composite <strong style={{ color: scoreColor(sig.composite_signal_score) }}>{sig.composite_signal_score}</strong>
          {sig.soonest_impact_years != null && <> · soonest ~{sig.soonest_impact_years}y</>}
        </span>}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
          {(sig?.signals || []).map(s => {
            const PIcon = PROJECT_ICON[s.project_type] || Radio
            const sCol = STATUS_COLOR[s.status] || '#6B7280'
            return (
              <div key={s.id} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 13px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <PIcon size={13} color="#4338CA" strokeWidth={2} />
                  <span style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-primary)' }}>{PROJECT_LABEL[s.project_type] || 'Project'}</span>
                  <span style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.3px', color: sCol, background: `${sCol}14`, border: `1px solid ${sCol}28`, padding: '1px 7px', borderRadius: 100 }}>
                    {pretty(s.status)}
                  </span>
                  <span style={{ marginLeft: 'auto', fontSize: 11, color: '#9CA3AF', fontWeight: 500 }}>~{s.lead_time_years}y lead</span>
                </div>
                <div style={{ fontSize: 12.5, color: '#6B7280', lineHeight: 1.55, marginBottom: 8 }}>{s.headline}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div className="progress-bar" style={{ flex: 1 }}>
                    <div className="progress-fill" style={{ width: `${s.impact_score}%`, background: `linear-gradient(90deg, ${scoreColor(s.impact_score)}80, ${scoreColor(s.impact_score)})` }} />
                  </div>
                  <span style={{ fontSize: 11.5, fontWeight: 700, color: scoreColor(s.impact_score), width: 64, textAlign: 'right' }}>impact {s.impact_score}</span>
                  <span style={{ fontSize: 10.5, color: '#9CA3AF', width: 86, textAlign: 'right' }}>{s.source}</span>
                </div>
              </div>
            )
          })}
        </div>
        <div style={{ marginTop: 14 }}>
          <ProvenanceStrip kind="heuristic" provenance={{ source: 'Classical NLP (TF-IDF + rules)' }} note="TF-IDF + cosine retrieval + regex extraction over a curated sample corpus — not an LLM/transformer." />
        </div>
      </Panel>

      {/* ── Satellite / CV urban-growth ── */}
      <Panel icon={Satellite} title="Urban-Growth Raster (CV)" accent="#059669"
        badge={cv?.dominant_growth_direction && <span style={{ fontSize: 12, color: '#6B7280', fontWeight: 600 }}>
          growth → <strong style={{ color: '#059669' }}>{cv.dominant_growth_direction.compass}</strong> · sprawl {cv.sprawl_index}
        </span>}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
          {imgOk ? (
            <img
              src={cvRasterUrl(cityId)}
              alt="Urban growth raster"
              onError={() => setImgOk(false)}
              style={{ width: 260, height: 260, borderRadius: 12, border: '1px solid var(--border-faint)', flexShrink: 0, objectFit: 'cover' }}
            />
          ) : (
            <div style={{ width: 260, height: 260, borderRadius: 12, border: '1px dashed var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 16, color: '#9CA3AF', fontSize: 12.5, flexShrink: 0 }}>
              Raster needs the backend running<br />(start it on :8000)
            </div>
          )}
          <div style={{ flex: 1, minWidth: 200 }}>
            <div className="section-title" style={{ marginBottom: 10 }}>Built-up Area by Year</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
              {(() => {
                const rows = cv?.per_year || []
                const maxA = Math.max(1, ...rows.map(r => r.area_sqkm))
                return rows.map(r => (
                  <div key={r.year} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 11.5, color: r.predicted ? '#4338CA' : '#6B7280', width: 52, fontWeight: r.predicted ? 700 : 500 }}>
                      {r.year}{r.predicted ? '*' : ''}
                    </span>
                    <div className="progress-bar" style={{ flex: 1 }}>
                      <div className="progress-fill" style={{ width: `${(r.area_sqkm / maxA) * 100}%`, background: r.predicted ? 'linear-gradient(90deg,#a5b4fc,#4338CA)' : 'linear-gradient(90deg,#5eead4,#0D9488)' }} />
                    </div>
                    <span style={{ fontSize: 11.5, color: '#374151', width: 66, textAlign: 'right', fontWeight: 600 }}>{r.area_sqkm} km²</span>
                  </div>
                ))
              })()}
            </div>
            <div style={{ fontSize: 11, color: '#9CA3AF', marginTop: 10, lineHeight: 1.5 }}>
              {cv?.method?.includes('mock') ? 'Offline estimate.' : 'Anisotropic rasterisation + scipy.ndimage morphology.'} <span style={{ color: '#4338CA' }}>*</span> = predicted (2031).
            </div>
          </div>
        </div>
        <div style={{ marginTop: 14 }}>
          <ProvenanceStrip kind="simulated" provenance={{ source: 'CV morphology on procedural masks' }} note="Real scipy.ndimage morphology over procedurally-generated urban masks — NOT satellite imagery segmentation." />
        </div>
      </Panel>
    </div>
  )
}
