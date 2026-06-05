import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { TrendingUp, Code2, Check, ArrowRight, Cpu, Activity, Satellite, Globe2, Mail, BookOpen, AlertCircle } from 'lucide-react'

const TIERS = [
  {
    name: 'Developer', price: '₹0', unit: '/forever', highlight: false,
    blurb: 'For prototypes & evaluation',
    // 1,000 req/day  =  tiers.py daily_quota=1_000
    features: ['1,000 API calls / day', 'All city & prediction endpoints', 'Community support'],
    cta: 'Start free', ctaTo: '/register',
  },
  {
    name: 'Pro', price: '₹1,499', unit: '/month', highlight: true,
    blurb: 'For products & startups',
    // 5,000 req/day / 50,000 req/month  =  tiers.py
    features: ['5,000 API calls / day (50,000 / month)', 'XGBoost · NLP · CV · GeoJSON', 'Advanced forecasts + export', 'Email support'],
    cta: 'Get API key', ctaTo: '/register',
  },
  {
    name: 'Enterprise', price: 'Custom', unit: '', highlight: false,
    blurb: 'For platforms & institutions',
    features: ['High-volume + SLA', 'Org accounts & team analytics', 'Dedicated support & onboarding'],
    cta: 'Contact sales', ctaTo: 'mailto:api@landai.in',
  },
]

const ENDPOINTS = [
  { icon: Cpu, label: 'GET /api/ml/price/{city}', desc: 'XGBoost land-price forecast' },
  { icon: Activity, label: 'GET /api/signals/{city}', desc: 'NLP infrastructure signals' },
  { icon: Satellite, label: 'GET /api/cv/{city}/metrics', desc: 'CV urban-growth metrics' },
  { icon: Globe2, label: 'GET /api/geo/nearby', desc: 'Nearest-cities (GPS) lookup' },
]

export default function Footer() {
  return (
    <footer style={{ background: '#0E1116', color: '#C7CBD1', marginTop: 40 }}>
      {/* ── Developer / API band ── */}
      <div id="developers" style={{ maxWidth: 1340, margin: '0 auto', padding: '56px 24px 8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 7,
            background: 'rgba(20,184,166,0.12)', border: '1px solid rgba(20,184,166,0.3)',
            color: '#5eead4', borderRadius: 100, padding: '5px 13px', fontSize: 12, fontWeight: 600,
          }}>
            <Code2 size={13} /> DEVELOPERS
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 16, marginBottom: 28 }}>
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 800, color: '#fff', fontFamily: 'DM Sans, sans-serif', letterSpacing: '-0.6px', lineHeight: 1.15 }}>
              Build on the LandAI API
            </h2>
            <p style={{ fontSize: 15, color: '#9aa1ab', marginTop: 8, maxWidth: 560, lineHeight: 1.6 }}>
              Urban-growth prediction for 116 Indian cities — land-price ML, infrastructure-signal NLP,
              spatial GeoJSON and computer-vision growth rasters, all over one REST API.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <a href="mailto:api@landai.in?subject=LandAI%20API%20key" className="btn btn-teal" style={{ textDecoration: 'none' }}>
              <Mail size={15} /> Get an API key
            </a>
            <Link to="/docs" className="btn btn-outline"
               style={{ textDecoration: 'none', background: 'transparent', color: '#C7CBD1', borderColor: 'rgba(255,255,255,0.18)' }}>
              <BookOpen size={15} /> API docs
            </Link>
          </div>
        </div>

        {/* endpoint teaser */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10, marginBottom: 36 }}>
          {ENDPOINTS.map(({ icon: Icon, label, desc }) => (
            <div key={label} style={{ background: '#161A21', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 12, padding: '13px 15px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <Icon size={14} color="#5eead4" />
                <code style={{ fontSize: 12, color: '#e5e7eb', fontFamily: 'ui-monospace, Menlo, monospace' }}>{label}</code>
              </div>
              <div style={{ fontSize: 12, color: '#7d838d' }}>{desc}</div>
            </div>
          ))}
        </div>

        {/* billing not-live disclaimer */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14, background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 10, padding: '8px 14px', fontSize: 12.5, color: '#D97706' }}>
          <AlertCircle size={14} style={{ flexShrink: 0 }} />
          <span>Billing is <strong>not live</strong> — prices shown are the planned architecture only. No charges occur today. <Link to="/register" style={{ color: '#D97706', fontWeight: 700 }}>Create a free account</Link> to get started.</span>
        </div>
        {/* pricing tiers */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14, marginBottom: 8 }}>
          {TIERS.map(t => (
            <motion.div key={t.name}
              whileHover={{ y: -4 }}
              style={{
                background: t.highlight ? 'linear-gradient(160deg, #14342f, #161A21)' : '#161A21',
                border: `1px solid ${t.highlight ? 'rgba(20,184,166,0.45)' : 'rgba(255,255,255,0.08)'}`,
                borderRadius: 16, padding: '20px 20px 22px', position: 'relative',
              }}>
              {t.highlight && (
                <span style={{
                  position: 'absolute', top: -10, right: 16, background: 'linear-gradient(135deg,#14B8A6,#0D9488)',
                  color: '#06231f', fontSize: 10.5, fontWeight: 800, letterSpacing: '0.5px',
                  padding: '3px 10px', borderRadius: 100, textTransform: 'uppercase',
                }}>Popular</span>
              )}
              <div style={{ fontSize: 13, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{t.name}</div>
              <div style={{ fontSize: 12.5, color: '#7d838d', marginTop: 2, marginBottom: 12 }}>{t.blurb}</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 16 }}>
                <span style={{ fontSize: 30, fontWeight: 800, color: '#fff', fontFamily: 'DM Sans, sans-serif', letterSpacing: '-1px' }}>{t.price}</span>
                <span style={{ fontSize: 13, color: '#7d838d' }}>{t.unit}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 9, marginBottom: 18 }}>
                {t.features.map(f => (
                  <div key={f} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#C7CBD1' }}>
                    <Check size={14} color="#14B8A6" style={{ flexShrink: 0 }} /> {f}
                  </div>
                ))}
              </div>
              {t.ctaTo?.startsWith('mailto') ? (
                <a href={t.ctaTo} style={{ textDecoration: 'none' }}>
                  <div className="btn" style={{ width: '100%', background: 'transparent', color: '#C7CBD1', border: '1px solid rgba(255,255,255,0.18)' }}>
                    {t.cta} <ArrowRight size={14} />
                  </div>
                </a>
              ) : (
                <Link to={t.ctaTo || '/register'} style={{ textDecoration: 'none' }}>
                  <div className="btn" style={{
                    width: '100%',
                    background: t.highlight ? 'linear-gradient(135deg,#14B8A6,#0D9488)' : 'transparent',
                    color: t.highlight ? '#fff' : '#C7CBD1',
                    border: t.highlight ? 'none' : '1px solid rgba(255,255,255,0.18)',
                  }}>
                    {t.cta} <ArrowRight size={14} />
                  </div>
                </Link>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* ── Link columns ── */}
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)', marginTop: 36 }}>
        <div style={{ maxWidth: 1340, margin: '0 auto', padding: '36px 24px 28px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 28 }}>
          {/* Brand */}
          <div style={{ minWidth: 200 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <div style={{
                width: 34, height: 34, borderRadius: 10,
                background: 'linear-gradient(135deg, #4338CA 0%, #0D9488 100%)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <TrendingUp size={17} color="#fff" strokeWidth={2.5} />
              </div>
              <span style={{ fontWeight: 800, fontSize: 18, color: '#fff', fontFamily: 'DM Sans, sans-serif' }}>
                Land<span style={{ color: '#5eead4' }}>AI</span>
              </span>
            </div>
            <p style={{ fontSize: 13, color: '#7d838d', lineHeight: 1.65, maxWidth: 240 }}>
              AI-powered urban-growth & land-value prediction for India's Tier 2 / Tier 3 cities.
            </p>
          </div>

          {[
            { h: 'Product', links: [['Explore Map', '/'], ['City Analysis', '/city/tirupati'], ['Compare Cities', '/compare']] },
            { h: 'Developers', links: [['API Docs', '/docs'], ['Pricing', '#developers'], ['Register free', '/register'], ['Get API Key', 'mailto:api@landai.in', true]] },
            { h: 'Company', links: [['About', '#'], ['Vision', '#'], ['Contact', 'mailto:api@landai.in', true]] },
          ].map(col => (
            <div key={col.h}>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.7px', marginBottom: 14 }}>{col.h}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {col.links.map(([label, to, external]) => external
                  ? <a key={label} href={to} target={to.startsWith('mailto') ? undefined : '_blank'} rel="noreferrer" style={{ fontSize: 13, color: '#9aa1ab' }}>{label}</a>
                  : to.startsWith('#')
                    ? <a key={label} href={to} style={{ fontSize: 13, color: '#9aa1ab' }}>{label}</a>
                    : <Link key={label} to={to} style={{ fontSize: 13, color: '#9aa1ab' }}>{label}</Link>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* bottom bar */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}>
          <div style={{ maxWidth: 1340, margin: '0 auto', padding: '18px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
            <span style={{ fontSize: 12.5, color: '#6b7178' }}>© {new Date().getFullYear()} LandAI · 116 cities · 25 states</span>
            <span style={{ fontSize: 11.5, color: '#5b616a', maxWidth: 560, textAlign: 'right' }}>
              Forecasts are data-driven estimates for research, not investment advice. Figures are curated approximations, not live market quotes.
            </span>
          </div>
        </div>
      </div>
    </footer>
  )
}
