import axios from 'axios'
import {
  MOCK_CITIES, MOCK_STATES,
  getMockFullAnalysis, getMockSimilarCities,
  getMockMlPrice, getMockSignals, getMockCvMetrics, getMockGeoZones,
  getMockScore, getMockCopilot,
} from './mockData'

const BASE = '/api'

const api = axios.create({ baseURL: BASE, timeout: 6000 })

// ── Data-trust event bus: make fallbacks NON-silent ─────────────────────────
const _apiListeners = new Set()
export const subscribeApiEvents = (cb) => {
  _apiListeners.add(cb)
  return () => _apiListeners.delete(cb)
}
const _emit = (evt) => { _apiListeners.forEach((cb) => { try { cb(evt) } catch { /* noop */ } }) }

api.interceptors.response.use(
  (resp) => { _emit({ type: 'online' }); return resp },
  (error) => {
    const resp = error.response
    if (resp && resp.status === 429) {
      const retry = Number(resp.headers?.['retry-after']) || resp.data?.retry_after_seconds || 30
      _emit({ type: 'ratelimited', retryAfter: retry })
    } else {
      // server responded (even other 4xx) => reachable; no response => network/timeout => offline
      _emit({ type: resp ? 'online' : 'offline' })
    }
    return Promise.reject(error)
  },
)

// System / data-trust health — NO .catch, so the trust context detects offline via rejection.
export const fetchSystemHealth = () => api.get('/system/health').then((r) => r.data)

// Live OSM amenities — returns the provenance-wrapped envelope, or an honest
// {available:false} on failure (we never substitute fabricated numbers).
export const fetchLiveAmenities = (cityId, { radius_m, max_pois = 40 } = {}) => {
  const params = { max_pois }
  if (radius_m) params.radius_m = radius_m
  return api.get(`/live/amenities/${cityId}`, { params })
    .then((r) => r.data)
    .catch(() => ({
      available: false,
      source: 'OpenStreetMap (Overpass API)',
      source_key: 'osm_overpass',
      reason: 'Backend or live source unreachable',
    }))
}

// ── Auth token + authenticated platform API ─────────────────────────────────
let _authToken = (typeof localStorage !== 'undefined' && localStorage.getItem('landai_token')) || null
export const setAuthToken = (t) => {
  _authToken = t || null
  try { t ? localStorage.setItem('landai_token', t) : localStorage.removeItem('landai_token') } catch { /* ignore */ }
}
export const getAuthToken = () => _authToken
api.interceptors.request.use((cfg) => {
  if (_authToken) cfg.headers.Authorization = `Bearer ${_authToken}`
  return cfg
})

export const registerUser = (email, password) => api.post('/auth/register', { email, password }).then(r => r.data)
export const loginUser = (email, password) => api.post('/auth/login', { email, password }).then(r => r.data)
export const fetchMe = () => api.get('/auth/me').then(r => r.data)
export const logoutUser = () => {
  // Real server-side logout: revoke the presented refresh session.
  const refresh = (typeof localStorage !== 'undefined' && localStorage.getItem('landai_refresh')) || null
  return api.post('/auth/logout', refresh ? { refresh_token: refresh } : {}).then(r => r.data).catch(() => ({}))
}
export const logoutAllApi = () => api.post('/auth/logout-all').then(r => r.data).catch(() => ({}))
export const listSessions = () => api.get('/account/sessions').then(r => r.data)
export const revokeSession = (id) => api.delete(`/account/sessions/${id}`).then(r => r.data)
export const fetchUsage = () => api.get('/account/usage').then(r => r.data)
export const fetchTiers = () => api.get('/auth/tiers').then(r => r.data)
export const listApiKeys = () => api.get('/keys').then(r => r.data)
export const createApiKey = (name) => api.post('/keys', { name }).then(r => r.data)
export const regenApiKey = (id) => api.post(`/keys/${id}/regenerate`).then(r => r.data)
export const revokeApiKey = (id) => api.delete(`/keys/${id}`).then(r => r.data)
export const listSavedCities = () => api.get('/account/saved-cities').then(r => r.data)
export const saveCityApi = (city_id, note = '') => api.post('/account/saved-cities', { city_id, note }).then(r => r.data)
export const unsaveCityApi = (city_id) => api.delete(`/account/saved-cities/${city_id}`).then(r => r.data)

// Persistent product platform: watchlist · compare history · saved searches
export const listWatchlist = () => api.get('/account/watchlist').then(r => r.data)
export const addWatchApi = (city_id) => api.post('/account/watchlist', { city_id }).then(r => r.data)
export const removeWatchApi = (city_id) => api.delete(`/account/watchlist/${city_id}`).then(r => r.data)
export const listCompareHistory = (limit = 20) => api.get('/account/compare-history', { params: { limit } }).then(r => r.data)
export const recordCompareApi = (city_a, city_b) => api.post('/account/compare-history', { city_a, city_b }).then(r => r.data)
export const deleteCompareApi = (id) => api.delete(`/account/compare-history/${id}`).then(r => r.data)
export const listSavedSearches = () => api.get('/account/saved-searches').then(r => r.data)
export const saveSearchApi = (label, query) => api.post('/account/saved-searches', { label, query }).then(r => r.data)
export const deleteSavedSearchApi = (id) => api.delete(`/account/saved-searches/${id}`).then(r => r.data)
export const fetchDashboard = () => api.get('/account/dashboard').then(r => r.data)
export const fetchUsageHistory = (days = 30) => api.get('/account/usage-history', { params: { days } }).then(r => r.data)

// Admin (role=admin) platform analytics + security
export const fetchQuotaMetrics = () => api.get('/system/quota-metrics').then(r => r.data)
export const fetchAuthMetrics = () => api.get('/system/auth-metrics').then(r => r.data)
export const fetchAuditTrail = (limit = 100) => api.get('/system/audit', { params: { limit } }).then(r => r.data)
export const triggerUsageRollup = () => api.post('/system/usage-rollup').then(r => r.data)

// ML governance / model card
export const fetchModelCard = () => api.get('/ml/model-info').then(r => r.data)
export const fetchLeakageAudit = () => api.get('/ml/leakage-audit').then(r => r.data)
export const fetchModelRegistry = () => api.get('/ml/registry').then(r => r.data)
export const fetchDriftBaseline = () => api.get('/ml/drift').then(r => r.data)
export const promoteModel = (version) => api.post(`/ml/registry/${version}/promote`).then(r => r.data)
export const archiveModel = (version) => api.post(`/ml/registry/${version}/archive`).then(r => r.data)
export const fetchObservability = () => api.get('/system/observability').then(r => r.data)

// ── Fallback-aware wrappers ────────────────────────────────────────────────
export const fetchAllCities = () =>
  api.get('/cities/').then(r => r.data).catch(() => MOCK_CITIES)

export const fetchCity = (id) =>
  api.get(`/cities/${id}`).then(r => r.data)
    .catch(() => MOCK_CITIES.find(c => c.id === id) || MOCK_CITIES[0])

export const searchCities = ({ q = '', state = '', tier } = {}) => {
  const params = {}
  if (q) params.q = q
  if (state) params.state = state
  if (tier != null) params.tier = tier
  return api.get('/cities/', { params }).then(r => r.data).catch(() => {
    return MOCK_CITIES.filter(c =>
      (!q     || c.name.toLowerCase().includes(q.toLowerCase()) || c.id.includes(q.toLowerCase())) &&
      (!state || c.state === state) &&
      (tier == null || c.tier === Number(tier))
    )
  })
}

export const fetchStates = () =>
  api.get('/cities/states').then(r => r.data).catch(() => MOCK_STATES)

export const fetchPrediction = (id, horizon = 15) =>
  api.get(`/predictions/${id}`, { params: { horizon } }).then(r => r.data)
    .catch(() => getMockFullAnalysis(id).prediction)

export const fetchFullAnalysis = (id) =>
  api.get(`/predictions/${id}/full`).then(r => r.data)
    .catch(() => getMockFullAnalysis(id))

export const fetchSimilarCities = (id, top = 5) =>
  api.get(`/predictions/${id}/similar`, { params: { top } }).then(r => r.data)
    .catch(() => getMockSimilarCities(id, top))

export const fetchTwin = (id) =>
  api.get(`/predictions/${id}/twin`).then(r => r.data)
    .catch(() => getMockFullAnalysis(id).twin)

// ── AI / NLP / Geo / CV feature endpoints (fallback-aware) ──────────────────
export const fetchMlPrice = (id, horizon = 10) =>
  api.get(`/ml/price/${id}`, { params: { horizon } }).then(r => r.data)
    .catch(() => getMockMlPrice(id, horizon))

export const fetchMlModelInfo = () =>
  api.get('/ml/model-info').then(r => r.data)
    .catch(() => ({ backend: 'mock-fallback', n_samples: MOCK_CITIES.length, train_r2: null, cv_r2_5fold: null, feature_importances: [], features: [] }))

export const fetchSignals = (id, top = 6) =>
  api.get(`/signals/${id}`, { params: { top } }).then(r => r.data)
    .catch(() => getMockSignals(id, top))

export const fetchCvMetrics = (id) =>
  api.get(`/cv/${id}/metrics`).then(r => r.data)
    .catch(() => getMockCvMetrics(id))

export const fetchGeoZones = (id) =>
  api.get(`/geo/city/${id}/zones.geojson`).then(r => r.data)
    .catch(() => getMockGeoZones(id))

// Direct image URL (served by the backend via the Vite proxy)
export const cvRasterUrl = (id) => `${BASE}/cv/${id}/growth-raster.png`

export const fetchScore = (id) =>
  api.get(`/score/${id}`).then(r => r.data).catch(() => getMockScore(id))

export const fetchNearby = (lat, lng, top = 8, radius_km = 400) =>
  api.get('/geo/nearby', { params: { lat, lng, top, radius_km } }).then(r => r.data)
    .catch(() => ({ backend: 'mock', detected_region: null, results: [] }))

export const runCopilot = (query, top = 6) =>
  api.post('/copilot/query', { query, top }).then(r => r.data)
    .catch(() => getMockCopilot(query, top))

export const formatPrice = (p) => {
  if (p >= 100000) return `₹${(p / 100000).toFixed(1)}L`
  if (p >= 1000)   return `₹${(p / 1000).toFixed(1)}K`
  return `₹${p}`
}

export const formatArea = (a) =>
  a >= 1000 ? `${(a / 1000).toFixed(1)}K km²` : `${a.toFixed(1)} km²`

export const phaseColor = (phase) => ({
  emerging: '#22c55e',
  accelerating: '#3b82f6',
  maturing: '#f97316',
  mature: '#94a3b8'
})[phase] || '#94a3b8'

export const tierColor = (tier) => ({
  1: '#ef4444',
  2: '#f97316',
  3: '#22c55e'
})[tier] || '#94a3b8'

export const scoreColor = (score) => {
  if (score >= 75) return '#22c55e'
  if (score >= 55) return '#3b82f6'
  if (score >= 40) return '#f97316'
  return '#94a3b8'
}
