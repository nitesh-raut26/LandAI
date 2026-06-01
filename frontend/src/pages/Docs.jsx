import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BookOpen, Code2, Lock, CheckCircle2, ChevronRight, AlertCircle, Copy, Check, ExternalLink, Cpu, Activity, Satellite, Globe2, MapPinned, Shield, Zap, Users, ArrowRight } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

// ── Colour helpers matching the design system ─────────────────────────────
const TIER_COLOR = { developer: '#4338CA', pro: '#059669', enterprise: '#D97706' }
const METHOD_COLOR = { GET: '#0D9488', POST: '#4338CA', DELETE: '#EF4444' }

// ── API reference ─────────────────────────────────────────────────────────
const SECTIONS = [
  {
    id: 'overview', label: 'Overview', icon: BookOpen,
  },
  {
    id: 'auth', label: 'Authentication', icon: Shield,
    endpoints: [],
  },
  {
    id: 'free-api', label: 'Free API', icon: Globe2,
    badge: 'Free',
    endpoints: [
      { method: 'GET', path: '/api/cities/', desc: 'List all 116 cities with filters (?q=, ?state=, ?tier=)', tier: 'developer', params: [{ k: 'q', d: 'Search name or state' }, { k: 'tier', d: '1, 2, or 3' }, { k: 'state', d: 'e.g. Maharashtra' }] },
      { method: 'GET', path: '/api/cities/{city_id}', desc: 'Full city record — coordinates, population, land price, scores', tier: 'developer' },
      { method: 'GET', path: '/api/predictions/{city_id}/full', desc: 'History + growth forecast + twin-city trajectory', tier: 'developer' },
      { method: 'GET', path: '/api/score/{city_id}', desc: 'Investment scoring — ROI, risk, liquidity, demand, SHAP drivers', tier: 'developer' },
      { method: 'GET', path: '/api/signals/{city_id}', desc: 'NLP infrastructure signals (TF-IDF + rules over curated corpus)', tier: 'developer' },
    ],
  },
  {
    id: 'metered', label: 'Metered API (v1)', icon: Zap,
    badge: 'API Key',
    endpoints: [
      { method: 'GET', path: '/api/v1/city/{city_id}', desc: 'City summary — tier, phase, coordinates, price 2021', tier: 'developer' },
      { method: 'GET', path: '/api/v1/ml/{city_id}', desc: 'XGBoost CAGR forecast + 90% conformal interval + TreeSHAP + price trajectory', tier: 'developer' },
      { method: 'GET', path: '/api/v1/score/{city_id}', desc: 'Full investment scoring (ROI · risk · liquidity · future-dev)', tier: 'developer' },
    ],
  },
  {
    id: 'live', label: 'Live Data (OSM)', icon: MapPinned,
    badge: 'Live',
    endpoints: [
      { method: 'GET', path: '/api/live/amenities/{city_id}', desc: 'Real-time OSM amenities — counts by type, derived scores, provenance + freshness', tier: 'developer', params: [{ k: 'radius_m', d: '500–60000 (default 8000)' }, { k: 'max_pois', d: 'max POIs in sample (default 60)' }] },
      { method: 'GET', path: '/api/live/amenities', desc: 'Same for any lat/lng', tier: 'developer', params: [{ k: 'lat', d: 'latitude (required)' }, { k: 'lng', d: 'longitude (required)' }] },
      { method: 'GET', path: '/api/live/sources', desc: 'Source registry + ToS-gate demonstration', tier: 'developer' },
    ],
  },
  {
    id: 'system', label: 'System / Observability', icon: Activity,
    endpoints: [
      { method: 'GET', path: '/api/system/health', desc: 'Liveness probe — degraded-systems list, persistence mode', tier: 'developer' },
      { method: 'GET', path: '/api/system/provenance', desc: 'Machine-readable honesty matrix (real/curated/heuristic/simulated)', tier: 'developer' },
      { method: 'GET', path: '/api/system/metrics', desc: 'Per-endpoint latency (p50/p95), cache hit/miss, ingestion counters, model-inference timer', tier: 'pro' },
      { method: 'GET', path: '/api/system/performance', desc: 'SLA summary — error rate, slowest endpoints, rate-limited count', tier: 'pro' },
      { method: 'GET', path: '/api/system/auth-metrics', desc: 'Auth counters — signups / logins / failures / active keys (no PII)', tier: 'enterprise', rbac: 'admin' },
    ],
  },
  {
    id: 'advanced', label: 'Advanced (Pro+)', icon: Cpu,
    badge: 'Pro',
    endpoints: [
      { method: 'GET', path: '/api/ml/price/{city_id}', desc: 'XGBoost price model — full trajectory + 90% conformal interval + SHAP, direct (no quota)', tier: 'pro' },
      { method: 'GET', path: '/api/cv/{city_id}/metrics', desc: 'CV morphology — compactness, fragmentation, dominant growth bearing (procedural masks)', tier: 'pro' },
      { method: 'GET', path: '/api/geo/city/{city_id}/zones.geojson', desc: 'Growth-zone polygons — current extent + 5/10-yr directional sectors (shapely)', tier: 'pro' },
    ],
  },
  {
    id: 'changelog', label: 'Changelog', icon: CheckCircle2,
  },
]

const CHANGELOG = [
  { v: '2.0.0', date: '2026-06', items: ['JWT auth + hashed API keys + RBAC', 'Metered /api/v1 Developer API with quota headers', 'Subscription tiers (Developer/Pro/Enterprise) — billing scaffold only', 'Saved cities (server-side persistence)'] },
  { v: '1.9.0', date: '2026-06', items: ['Inbound per-IP rate limiting (token bucket, 429 + Retry-After)', 'Request-ID + timing middleware + /api/system/metrics', 'Inline provenance strips on all AI panels (Heuristic/Model/Simulated/Live badges)', '429 frontend banner (auto-clears)'] },
  { v: '1.8.0', date: '2026-06', items: ['Real OSM live ingestion (Overpass + Nominatim), provenance envelopes', 'CV+ conformal prediction intervals on XGBoost (90% nominal, 92.2% empirical OOF)', 'Data Trust Layer — BackendHealthBanner, DataStatusBadge, no silent fallback'] },
  { v: '1.0.0', date: '2026-05', items: ['116 Indian cities, 25 states/UTs', 'XGBoost + TreeSHAP, NLP signals, CV raster, shapely GeoJSON', 'React frontend with map, heatmap, copilot, analytics'] },
]

// ── Tiny components ───────────────────────────────────────────────────────
function TierBadge({ tier, rbac }) {
  const color = TIER_COLOR[tier] || '#6B7280'
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.4px', padding: '2px 8px', borderRadius: 100, background: `${color}14`, color, border: `1px solid ${color}28` }}>
      {rbac ? <><Lock size={9} /> {rbac}</> : tier}
    </span>
  )
}

function MethodBadge({ method }) {
  const c = METHOD_COLOR[method] || '#6B7280'
  return (
    <span style={{ fontSize: 10.5, fontWeight: 800, fontFamily: 'ui-monospace, monospace', padding: '2px 7px', borderRadius: 5, background: `${c}18`, color: c, border: `1px solid ${c}28`, letterSpacing: '0.3px', flexShrink: 0 }}>
      {method}
    </span>
  )
}

function CodeBlock({ code, language = 'bash' }) {
  const [copied, setCopied] = useState(false)
  const copy = () => { try { navigator.clipboard.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 1400) } catch { /* ignore */ } }
  return (
    <div style={{ position: 'relative', background: '#0E1116', border: '1px solid rgba(255,255,255,0.09)', borderRadius: 10, overflow: 'hidden', marginTop: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 12px', borderBottom: '1px solid rgba(255,255,255,0.07)', background: '#161A21' }}>
        <span style={{ fontSize: 11, color: '#6B7280', fontFamily: 'ui-monospace, monospace' }}>{language}</span>
        <button onClick={copy} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6B7280', display: 'flex', alignItems: 'center', gap: 5, fontSize: 11 }}>
          {copied ? <><Check size={12} color="#059669" /> Copied</> : <><Copy size={12} /> Copy</>}
        </button>
      </div>
      <pre style={{ margin: 0, padding: '12px 14px', fontSize: 12.5, color: '#e5e7eb', fontFamily: 'ui-monospace, Menlo, monospace', overflowX: 'auto', lineHeight: 1.6 }}>{code}</pre>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────
export default function Docs() {
  const { user } = useAuth()
  const [active, setActive] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const userTier = user?.subscription_tier || null
  const tierRank = { developer: 0, pro: 1, enterprise: 2 }
  const userRank = tierRank[userTier] ?? -1

  // 'unlocked'       – user can call this endpoint now
  // 'locked'         – logged in but needs a higher tier (show Upgrade)
  // 'requires_signup'– not logged in, tier restriction applies (show Sign up)
  const canAccess = (endpointTier) => {
    if (!endpointTier) return 'unlocked'   // no tier restriction → always open
    const required = tierRank[endpointTier] ?? 0
    if (!userTier) return required === 0 ? 'unlocked' : 'requires_signup'
    return userRank >= required ? 'unlocked' : 'locked'
  }

  const activeSection = SECTIONS.find(s => s.id === active)

  return (
    <div style={{ display: 'flex', minHeight: 'calc(100vh - 66px)', background: 'var(--bg-base)' }}>
      {/* ── Sidebar ── */}
      <aside style={{
        width: 220, flexShrink: 0, borderRight: '1px solid var(--border)',
        background: 'var(--bg-card)', position: 'sticky', top: 66, height: 'calc(100vh - 66px)',
        overflowY: 'auto', padding: '20px 0',
      }} className="docs-sidebar">
        <div style={{ padding: '0 16px 12px', borderBottom: '1px solid var(--border-faint)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <BookOpen size={14} color="var(--indigo)" />
            <span style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.6px', color: 'var(--text-muted)' }}>API Reference</span>
          </div>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 12, color: 'var(--text-secondary)' }}>
              <div style={{ width: 20, height: 20, borderRadius: '50%', background: 'linear-gradient(135deg,#4338CA,#0D9488)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 10, fontWeight: 800 }}>
                {user.email[0].toUpperCase()}
              </div>
              <span style={{ textTransform: 'capitalize', fontWeight: 600 }}>{user.subscription_tier}</span>
              <span style={{ color: 'var(--text-disabled)', fontWeight: 400 }}>plan</span>
            </div>
          ) : (
            <Link to="/register" style={{ fontSize: 12, color: 'var(--indigo)', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}>
              <ArrowRight size={12} /> Sign up free
            </Link>
          )}
        </div>
        <nav style={{ padding: '10px 0' }}>
          {SECTIONS.map(sec => {
            const Icon = sec.icon
            const isActive = active === sec.id
            return (
              <button key={sec.id} onClick={() => setActive(sec.id)} style={{
                width: '100%', display: 'flex', alignItems: 'center', gap: 8,
                padding: '8px 16px', border: 'none', background: isActive ? 'rgba(67,56,202,0.08)' : 'transparent',
                borderLeft: isActive ? '3px solid var(--indigo)' : '3px solid transparent',
                color: isActive ? 'var(--indigo)' : 'var(--text-muted)',
                fontSize: 13.5, fontWeight: isActive ? 600 : 400, cursor: 'pointer', textAlign: 'left',
              }}>
                <Icon size={14} strokeWidth={1.8} style={{ flexShrink: 0 }} />
                {sec.label}
                {sec.badge && <span style={{ marginLeft: 'auto', fontSize: 10, fontWeight: 700, background: sec.id === 'metered' ? 'rgba(67,56,202,0.1)' : sec.id === 'advanced' ? 'rgba(5,150,105,0.1)' : 'rgba(13,148,136,0.1)', color: sec.id === 'advanced' ? '#059669' : sec.id === 'metered' ? 'var(--indigo)' : 'var(--teal)', borderRadius: 100, padding: '1px 7px' }}>{sec.badge}</span>}
              </button>
            )
          })}
        </nav>
        <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border-faint)', marginTop: 8 }}>
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--text-disabled)', textDecoration: 'none' }}>
            <ExternalLink size={12} /> Swagger UI
          </a>
        </div>
      </aside>

      {/* ── Main content ── */}
      <main style={{ flex: 1, maxWidth: 820, padding: '32px 32px 80px', overflowY: 'auto' }}>

        {/* ── Overview ── */}
        {active === 'overview' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <h1 style={{ fontSize: 28, fontWeight: 800, fontFamily: 'DM Sans', marginBottom: 10 }}>LandAI API</h1>
            <p style={{ fontSize: 15, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 24, maxWidth: 640 }}>
              Urban-growth prediction for 116 Indian cities — land-price ML (XGBoost + conformal intervals), infrastructure-signal NLP, spatial GeoJSON, CV raster, and live OpenStreetMap amenities over one REST API.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 28 }}>
              {[
                { label: 'Base URL', value: 'http://localhost:8000' },
                { label: 'Protocol', value: 'HTTPS / REST' },
                { label: 'Format', value: 'JSON' },
                { label: 'Auth', value: 'JWT Bearer + API Key' },
              ].map(({ label, value }) => (
                <div key={label} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 14px' }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-disabled)', textTransform: 'uppercase', letterSpacing: '0.4px', marginBottom: 4 }}>{label}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'ui-monospace, monospace' }}>{value}</div>
                </div>
              ))}
            </div>

            <div style={{ background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: 11, padding: '12px 16px', marginBottom: 24, fontSize: 13.5, color: '#B45309', lineHeight: 1.6 }}>
              <strong>Transparency notice:</strong> All data, forecasts, and scores are labelled by type — <strong>Live</strong> (real-time OSM), <strong>Curated</strong> (expert dataset), <strong>Model</strong> (trained ML), <strong>Heuristic</strong> (rule-based), or <strong>Simulated</strong> (procedural). See <code>/api/system/provenance</code>.
            </div>

            <h2 style={{ fontSize: 17, fontWeight: 700, marginBottom: 12, fontFamily: 'DM Sans' }}>Quick start</h2>
            <CodeBlock language="bash" code={`# Free — no auth needed
curl "http://localhost:8000/api/cities/?tier=2&state=Maharashtra"

# With API key (get one at /keys after signing up)
curl -H "X-API-Key: lk_live_YOUR_KEY" \\
     "http://localhost:8000/api/v1/ml/pune"
`} />

            <h2 style={{ fontSize: 17, fontWeight: 700, margin: '28px 0 12px', fontFamily: 'DM Sans' }}>Tiers &amp; access</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { tier: 'developer', label: 'Developer (free)', desc: '1,000 req/day — all free endpoints + metered /api/v1 with API key', color: TIER_COLOR.developer },
                { tier: 'pro', label: 'Pro', desc: '5,000 req/day (50,000/month) — + advanced forecasts, export, analytics', color: TIER_COLOR.pro },
                { tier: 'enterprise', label: 'Enterprise', desc: 'High-volume + SLA — org accounts, dedicated support', color: TIER_COLOR.enterprise },
              ].map(({ tier, label, desc, color }) => {
                const access = canAccess(tier)
                return (
                  <div key={tier} style={{ display: 'flex', alignItems: 'center', gap: 12, background: 'var(--bg-card)', border: `1px solid ${access === 'locked' ? 'var(--border-faint)' : color + '30'}`, borderRadius: 11, padding: '11px 15px', opacity: access === 'locked' ? 0.65 : 1 }}>
                    {access === 'locked' ? <Lock size={15} color={color} style={{ flexShrink: 0 }} /> : <CheckCircle2 size={15} color={color} style={{ flexShrink: 0 }} />}
                    <div style={{ flex: 1 }}>
                      <span style={{ fontWeight: 700, fontSize: 14, color }}>{label}</span>
                      <span style={{ fontSize: 13, color: 'var(--text-muted)', marginLeft: 10 }}>{desc}</span>
                    </div>
                    {!userTier && tier === 'developer' && (
                      <Link to="/register" style={{ fontSize: 12, color, fontWeight: 700, textDecoration: 'none', whiteSpace: 'nowrap' }}>Sign up →</Link>
                    )}
                    {access === 'locked' && userTier && (
                      <span style={{ fontSize: 11, color: 'var(--text-disabled)', fontWeight: 600, textTransform: 'uppercase' }}>Upgrade</span>
                    )}
                  </div>
                )
              })}
            </div>

            {!user && (
              <div style={{ marginTop: 24, background: 'rgba(67,56,202,0.06)', border: '1px solid rgba(67,56,202,0.2)', borderRadius: 12, padding: '16px 18px' }}>
                <div style={{ fontWeight: 700, color: 'var(--indigo)', marginBottom: 6 }}>Get an API key in 30 seconds</div>
                <div style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginBottom: 12 }}>Create a free account → get an API key → start calling /api/v1. 1,000 requests/day, no credit card.</div>
                <Link to="/register" style={{ display: 'inline-flex', alignItems: 'center', gap: 7, padding: '9px 16px', borderRadius: 10, background: 'linear-gradient(135deg,#4338CA,#0D9488)', color: '#fff', fontWeight: 700, fontSize: 13.5, textDecoration: 'none' }}>
                  Create free account <ArrowRight size={14} />
                </Link>
              </div>
            )}
          </motion.div>
        )}

        {/* ── Authentication ── */}
        {active === 'auth' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, fontFamily: 'DM Sans', marginBottom: 10 }}>Authentication</h1>
            <p style={{ fontSize: 14.5, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 24, maxWidth: 600 }}>
              LandAI uses two authentication methods: <strong>JWT Bearer tokens</strong> for the web app, and <strong>API keys</strong> for the metered Developer API.
            </p>

            <h2 style={{ fontSize: 16, fontWeight: 700, margin: '0 0 10px', fontFamily: 'DM Sans' }}>JWT Bearer (web / interactive)</h2>
            <CodeBlock language="bash" code={`# 1. Register
curl -X POST http://localhost:8000/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"email":"you@example.com","password":"yourpassword"}'
# → {"access_token":"eyJ…","refresh_token":"eyJ…","token_type":"bearer"}

# 2. Call authenticated endpoints
curl -H "Authorization: Bearer eyJ…" \\
     http://localhost:8000/api/auth/me

# 3. Refresh (access token expires in 30 min)
curl -X POST http://localhost:8000/api/auth/refresh \\
  -d '{"refresh_token":"eyJ…"}'`} />

            <h2 style={{ fontSize: 16, fontWeight: 700, margin: '22px 0 10px', fontFamily: 'DM Sans' }}>API Key (programmatic / metered)</h2>
            <CodeBlock language="bash" code={`# 1. Create a key (requires JWT)
curl -X POST http://localhost:8000/api/keys \\
  -H "Authorization: Bearer eyJ…" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"production"}'
# → {"api_key":"lk_live_…","prefix":"lk_live_t21M…","id":1}
# Secret is shown ONCE — store it now.

# 2. Use the key on any /api/v1/* endpoint
curl -H "X-API-Key: lk_live_YOUR_KEY" \\
     http://localhost:8000/api/v1/city/pune`} />
            <div style={{ marginTop: 12, padding: '10px 14px', background: 'var(--bg-card2)', borderRadius: 9, border: '1px solid var(--border-faint)', fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>
              <strong>Security:</strong> API keys are stored as SHA-256 hashes — the plaintext is never logged or stored. Every successful API-key request returns quota headers: <code>X-Quota-Used</code>, <code>X-Quota-Remaining</code>, <code>X-RateLimit-Limit</code>.
            </div>

            <h2 style={{ fontSize: 16, fontWeight: 700, margin: '22px 0 10px', fontFamily: 'DM Sans' }}>Error responses</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { status: 401, label: 'Unauthorized', desc: 'Missing or invalid bearer token / API key.' },
                { status: 403, label: 'Forbidden', desc: 'Authenticated but insufficient role (e.g. non-admin hitting auth-metrics).' },
                { status: 429, label: 'Too Many Requests', desc: 'Rate limit exceeded (IP bucket) OR daily quota exhausted. See Retry-After header.' },
              ].map(({ status, label, desc }) => (
                <div key={status} style={{ display: 'flex', gap: 12, background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 9, padding: '10px 14px' }}>
                  <span style={{ fontFamily: 'ui-monospace, monospace', fontWeight: 800, color: '#EF4444', flexShrink: 0, fontSize: 13.5 }}>{status}</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 13.5, flexShrink: 0 }}>{label}</span>
                  <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{desc}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── Endpoint sections ── */}
        {activeSection?.endpoints && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, fontFamily: 'DM Sans', marginBottom: 8 }}>{activeSection.label}</h1>
            {active === 'metered' && (
              <div style={{ background: 'rgba(67,56,202,0.06)', border: '1px solid rgba(67,56,202,0.2)', borderRadius: 10, padding: '10px 14px', marginBottom: 20, fontSize: 13.5, color: 'var(--text-secondary)' }}>
                Requires an <strong>API key</strong> in the <code>X-API-Key</code> header. Quota is deducted per request. <Link to="/keys" style={{ color: 'var(--indigo)', fontWeight: 700 }}>Manage your keys →</Link>
              </div>
            )}
            {active === 'live' && (
              <div style={{ background: 'rgba(5,150,105,0.06)', border: '1px solid rgba(5,150,105,0.2)', borderRadius: 10, padding: '10px 14px', marginBottom: 20, fontSize: 13.5, color: '#065f46' }}>
                Returns a <strong>provenance envelope</strong> on every response — source, license, confidence, freshness. If the upstream is down, returns <code>available: false</code> (never fabricated data).
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {activeSection.endpoints.map(ep => {
                const access = canAccess(ep.tier)
                const isGated = access === 'locked' || access === 'requires_signup'
                const lockColor = access === 'requires_signup' ? 'var(--indigo)' : '#EF4444'
                return (
                  <div key={ep.path} style={{
                    background: 'var(--bg-card)',
                    border: `1px solid ${isGated ? (access === 'requires_signup' ? 'rgba(67,56,202,0.18)' : 'rgba(239,68,68,0.18)') : 'var(--border)'}`,
                    borderRadius: 13, overflow: 'hidden', opacity: isGated ? 0.8 : 1,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '13px 16px', flexWrap: 'wrap' }}>
                      <MethodBadge method={ep.method} />
                      <code style={{ flex: 1, fontSize: 13.5, fontFamily: 'ui-monospace, monospace', color: 'var(--text-primary)', wordBreak: 'break-all' }}>{ep.path}</code>
                      <TierBadge tier={ep.tier} rbac={ep.rbac} />
                      {isGated && <Lock size={13} color={lockColor} title={`Requires ${ep.tier} plan`} />}
                    </div>
                    <div style={{ padding: '0 16px 13px' }}>
                      <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.6 }}>{ep.desc}</p>
                      {ep.params?.length > 0 && (
                        <div style={{ marginTop: 10 }}>
                          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.4px', color: 'var(--text-disabled)', marginBottom: 6 }}>Query parameters</div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                            {ep.params.map(p => (
                              <div key={p.k} style={{ display: 'flex', gap: 10, fontSize: 12.5 }}>
                                <code style={{ color: 'var(--indigo)', fontFamily: 'ui-monospace, monospace', flexShrink: 0, fontWeight: 600 }}>{p.k}</code>
                                <span style={{ color: 'var(--text-muted)' }}>{p.d}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {/* RBAC gate — tailored per access state */}
                      {access === 'requires_signup' && (
                        <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, background: 'rgba(67,56,202,0.06)', borderRadius: 8, padding: '7px 11px', border: '1px solid rgba(67,56,202,0.15)' }}>
                          <Lock size={12} color="var(--indigo)" />
                          <span style={{ color: 'var(--text-secondary)' }}>Requires <strong>{ep.tier}</strong> plan</span>
                          <Link to="/register" style={{ marginLeft: 'auto', color: 'var(--indigo)', fontWeight: 700, fontSize: 12, whiteSpace: 'nowrap' }}>Sign up free →</Link>
                        </div>
                      )}
                      {access === 'locked' && (
                        <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, background: 'rgba(239,68,68,0.05)', borderRadius: 8, padding: '7px 11px', border: '1px solid rgba(239,68,68,0.15)' }}>
                          <Lock size={12} color="#EF4444" />
                          <span style={{ color: 'var(--text-secondary)' }}>Your <strong>{userTier}</strong> plan doesn't include this endpoint</span>
                          <Link to="/account" style={{ marginLeft: 'auto', color: '#EF4444', fontWeight: 700, fontSize: 12, whiteSpace: 'nowrap' }}>Upgrade →</Link>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}

        {/* ── Changelog ── */}
        {active === 'changelog' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <h1 style={{ fontSize: 24, fontWeight: 800, fontFamily: 'DM Sans', marginBottom: 24 }}>Changelog</h1>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
              {CHANGELOG.map(({ v, date, items }) => (
                <div key={v} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 13, padding: '16px 20px' }}>
                  <div style={{ display: 'flex', gap: 12, alignItems: 'baseline', marginBottom: 12 }}>
                    <span style={{ fontWeight: 800, fontSize: 16, fontFamily: 'DM Sans', color: 'var(--text-primary)' }}>v{v}</span>
                    <span style={{ fontSize: 12.5, color: 'var(--text-disabled)', fontWeight: 500 }}>{date}</span>
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 7 }}>
                    {items.map(item => (
                      <li key={item} style={{ display: 'flex', gap: 8, alignItems: 'flex-start', fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                        <ChevronRight size={14} color="var(--teal)" style={{ marginTop: 2, flexShrink: 0 }} />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </main>

      {/* responsive sidebar style */}
      <style>{`
        @media (max-width: 860px) {
          .docs-sidebar { display: none !important; }
        }
      `}</style>
    </div>
  )
}
