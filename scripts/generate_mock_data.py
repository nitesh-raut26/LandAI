#!/usr/bin/env python3
"""
Regenerate the frontend offline-fallback dataset from the live backend.

The frontend falls back to `frontend/src/utils/mockData.js` when the API is
unreachable. To keep the two in sync, this script pulls /api/cities from a
running backend and rewrites mockData.js (data + helpers + feature fallbacks).

Usage:
    # 1. start the backend (uvicorn app.main:app --port 8000)
    # 2. run:
    python scripts/generate_mock_data.py            # uses http://localhost:8000
    python scripts/generate_mock_data.py http://host:port
"""
import json
import os
import sys
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/") + "/api"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "frontend", "src", "utils", "mockData.js")

cities = json.load(urllib.request.urlopen(BASE + "/cities/", timeout=10))
states = json.load(urllib.request.urlopen(BASE + "/cities/states", timeout=10))

HELPERS = r"""
// ── Helpers (operate on the full backend-shape city objects above) ──────────
const _yrs = (o) => Object.keys(o).map(Number).sort((a, b) => a - b)
const _phaseRank = { emerging: 0, accelerating: 1, maturing: 2, mature: 3 }
const _bearing = { N: [1, 0], S: [-1, 0], E: [0, 1], W: [0, -1], NE: [0.7, 0.7], NW: [0.7, -0.7], SE: [-0.7, 0.7], SW: [-0.7, -0.7] }

function _genPrediction(city) {
  const baseYear = 2021, horizon = 15
  const curArea = city.urban_area_sqkm['2021']
  const curPrice = city.land_price_inr_per_sqft['2021']
  const cagrBase = { emerging: 0.115, accelerating: 0.09, maturing: 0.065, mature: 0.045 }[city.growth_phase] ?? 0.08
  const cagr = Math.min(Math.max(cagrBase + (city.tier === 3 ? 0.012 : 0) - (curPrice > 8000 ? 0.015 : 0), 0.03), 0.15)
  const aCagr = Math.min({ emerging: 0.045, accelerating: 0.032, maturing: 0.022, mature: 0.012 }[city.growth_phase] ?? 0.03, 0.055)
  const years = [], areas = [], prices = []
  for (let i = 0; i <= horizon; i++) {
    years.push(baseYear + i)
    areas.push(Math.round(curArea * Math.pow(1 + aCagr, i) * 100) / 100)
    prices.push(Math.round(curPrice * Math.pow(1 + cagr, i)))
  }
  const area5 = areas[5], area10 = areas[10], price5 = prices[5], price10 = prices[10]
  const dirs = (city.growth_directions && city.growth_directions.length ? city.growth_directions : ['N', 'E']).slice(0, 4)
  const phaseScore = { emerging: 88, accelerating: 72, maturing: 55, mature: 40 }[city.growth_phase] ?? 65
  const coslat = Math.max(Math.cos(city.lat * Math.PI / 180), 0.2)
  const rCur = Math.sqrt(curArea / Math.PI), r5 = Math.sqrt(area5 / Math.PI), r10 = Math.sqrt(area10 / Math.PI)
  const zones = []
  dirs.forEach((d, i) => {
    const [dy, dx] = _bearing[d] || [0, 0]
    const score = Math.min(phaseScore + (4 - i) * 3, 95)
    zones.push({ zone_id: `zone_${d.toLowerCase()}_5yr`, label: `${d} Corridor — 5-Year Zone`, direction: d, horizon_years: 5,
      radius_km: Math.round((r5 - rCur) * 100) / 100,
      center_lat: Math.round((city.lat + dy / 111 * r5 * 0.6) * 1e4) / 1e4,
      center_lng: Math.round((city.lng + dx / (111 * coslat) * r5 * 0.6) * 1e4) / 1e4,
      investment_score: score, expected_price_rise_pct: Math.round(phaseScore * 0.8 + 10),
      risk_level: score > 70 ? 'medium' : 'low', recommendation: score > 75 ? 'Buy Now' : 'Watch' })
    zones.push({ zone_id: `zone_${d.toLowerCase()}_10yr`, label: `${d} Fringe — 10-Year Zone`, direction: d, horizon_years: 10,
      radius_km: Math.round((r10 - r5) * 100) / 100,
      center_lat: Math.round((city.lat + dy / 111 * r10 * 0.7) * 1e4) / 1e4,
      center_lng: Math.round((city.lng + dx / (111 * coslat) * r10 * 0.7) * 1e4) / 1e4,
      investment_score: Math.max(score - 12, 40), expected_price_rise_pct: Math.round(phaseScore * 1.4 + 15),
      risk_level: ['emerging', 'accelerating'].includes(city.growth_phase) ? 'high' : 'medium',
      recommendation: ['emerging', 'accelerating'].includes(city.growth_phase) ? 'Buy Early' : 'Monitor' })
  })
  return {
    base_year: baseYear,
    annual_cagr_price_pct: Math.round(cagr * 1000) / 10,
    model: { type: 'calibrated_bounded_cagr(mock)', area_cagr_pct: Math.round(aCagr * 1000) / 10, price_cagr_pct: Math.round(cagr * 1000) / 10 },
    timeline: { years, urban_area_sqkm: areas, land_price_inr_per_sqft: prices },
    milestones: {
      area_2026_sqkm: area5, area_2031_sqkm: area10,
      price_2026_inr_per_sqft: price5, price_2031_inr_per_sqft: price10,
      price_appreciation_5yr_pct: Math.round((price5 / curPrice - 1) * 1000) / 10,
      price_appreciation_10yr_pct: Math.round((price10 / curPrice - 1) * 1000) / 10,
      confidence_5yr: 0.75, confidence_10yr: 0.5,
    },
    investment_zones: zones,
    growth_phase: city.growth_phase, investment_score: city.investment_score,
    city: { land_price_inr_per_sqft: city.land_price_inr_per_sqft },
  }
}

function _findTwin(city) {
  const cands = MOCK_CITIES.filter(c => c.id !== city.id && (_phaseRank[c.growth_phase] ?? 0) > (_phaseRank[city.growth_phase] ?? 0))
  const pool = (cands.length ? cands : MOCK_CITIES.filter(c => c.id !== city.id)).slice()
  pool.sort((a, b) => (b.state === city.state) - (a.state === city.state) || b.investment_score - a.investment_score)
  return pool[0]
}

export function getMockFullAnalysis(cityId) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const ay = _yrs(city.urban_area_sqkm), py = _yrs(city.land_price_inr_per_sqft)
  const history = { years: ay, urban_area_sqkm: ay.map(y => city.urban_area_sqkm[String(y)]) }
  const price_history = { years: py, values: py.map(y => city.land_price_inr_per_sqft[String(y)]) }
  const prediction = _genPrediction(city)
  const tw = _findTwin(city)
  const twinAy = _yrs(tw.urban_area_sqkm)
  const lag = { emerging: 18, accelerating: 12, maturing: 8, mature: 5 }[city.growth_phase] ?? 12
  const twin = {
    city_id: tw.id, city_name: tw.name, twin_city: tw, lag_years: lag,
    similarity_score: Math.min(95, 70 + Math.round(tw.investment_score * 0.25)),
    match_reason: 'Mock match — more-developed city with a comparable profile',
    twin_current_price: tw.land_price_inr_per_sqft['2021'],
    comparison: {
      city_a: { id: city.id, name: city.name, history: { area_years: ay, area_values: history.urban_area_sqkm } },
      city_b: { id: tw.id, name: tw.name, history: { area_years: twinAy, area_values: twinAy.map(y => tw.urban_area_sqkm[String(y)]) } },
    },
  }
  return { city, history, price_history, prediction, twin }
}

export function getMockSimilarCities(cityId, top = 6) {
  const city = MOCK_CITIES.find(c => c.id === cityId)
  const pool = city
    ? MOCK_CITIES.filter(c => c.id !== cityId)
        .map(c => ({ c, d: Math.abs(c.investment_score - city.investment_score) + (c.tier === city.tier ? 0 : 8) }))
        .sort((a, b) => a.d - b.d).map(x => x.c)
    : MOCK_CITIES
  return pool.slice(0, top).map((c, i) => ({
    city_id: c.id, name: c.name, state: c.state, tier: c.tier,
    growth_phase: c.growth_phase, investment_score: c.investment_score,
    similarity_score: Math.max(60, 94 - i * 5),
  }))
}

// ── Fallbacks for the AI / NLP / CV feature endpoints ───────────────────────
export function getMockMlPrice(cityId, horizon = 10) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const cagrBase = { emerging: 0.15, accelerating: 0.115, maturing: 0.08, mature: 0.055 }[city.growth_phase] ?? 0.10
  const cagr = Math.min(cagrBase + (city.tier === 3 ? 0.015 : 0), 0.30)
  const cur = city.land_price_inr_per_sqft['2021']
  const traj = []
  for (let i = 0; i <= horizon; i++) traj.push({ year: 2021 + i, price_inr_per_sqft: Math.round(cur * Math.pow(1 + cagr, i)) })
  return {
    city_id: city.id, model_backend: 'mock-fallback',
    predicted_annual_cagr_pct: Math.round(cagr * 1000) / 10,
    current_price_inr_per_sqft: cur,
    projected_price_5yr: traj[5]?.price_inr_per_sqft ?? traj[traj.length - 1].price_inr_per_sqft,
    projected_price_10yr: traj[traj.length - 1].price_inr_per_sqft,
    price_trajectory: traj,
    top_feature_contributions: [
      { feature: 'urban_area_cagr_01_21', contribution: 0.01 },
      { feature: 'economic_score', contribution: 0.004 },
      { feature: 'growth_phase_rank', contribution: -0.003 },
    ],
    feature_values: {},
  }
}

export function getMockSignals(cityId, top = 6) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const infra = city.infrastructure || {}
  const raw = []
  if (infra.has_airport) raw.push(['airport', 'operational', 1, `${city.name} has operational airport connectivity.`, 'AAI', 86])
  if ((city.government_schemes || []).some(s => /smart/i.test(s))) raw.push(['smart_city', 'approved', 3, `${city.name} is funded under the Smart City Mission.`, 'Smart City Mission', 70])
  if ((infra.num_national_highways || 0) >= 2) raw.push(['expressway', 'operational', 1, `${city.name} sits at a national highway junction.`, 'NHAI', 78])
  if (infra.has_railway) raw.push(['railway', 'approved', 4, `${city.name} railway station modernisation is underway.`, 'Indian Railways', 64])
  if (city.tier === 3 && city.growth_phase === 'emerging') raw.push(['realty', 'proposed', 6, `${city.name} is an emerging Tier-3 market with rising RERA registrations.`, 'RERA', 55])
  while (raw.length < 3) raw.push(['expressway', 'proposed', 5, `${city.name} regional road upgrades are proposed.`, 'State PWD', 50])
  const signals = raw.slice(0, top).map(([pt, st, lead, head, src, imp], i) => ({
    id: `mock_${city.id}_${i}`, project_type: pt, status: st, lead_time_years: lead,
    impact_score: imp, certainty: 0.7, headline: head, source: src, year: 2024, origin: 'mock',
    entities: { amounts_inr_crore: [], organizations: [src], locations: [city.name] },
  })).sort((a, b) => b.impact_score - a.impact_score)
  return {
    city_id: city.id, city_name: city.name, signal_count: signals.length,
    composite_signal_score: Math.round(signals.reduce((s, x) => s + x.impact_score, 0) / Math.max(signals.length, 1) * 10) / 10,
    soonest_impact_years: signals.length ? Math.min(...signals.map(s => s.lead_time_years)) : null,
    signals,
  }
}

export function getMockCvMetrics(cityId) {
  const city = MOCK_CITIES.find(c => c.id === cityId) || MOCK_CITIES[0]
  const ay = _yrs(city.urban_area_sqkm)
  return {
    city_id: city.id, city_name: city.name,
    grid: { resolution: 200, pixel_km: 0.2, window_km: 20 }, method: 'mock-fallback',
    per_year: ay.map(y => ({ year: y, area_sqkm: city.urban_area_sqkm[String(y)], compactness_polsby_popper: 0.95, fragmentation_components: 1 })),
    dominant_growth_direction: { compass: (city.growth_directions && city.growth_directions[0]) || 'N', bearing_deg: 0, offset_km: 1.5 },
    stated_growth_directions: city.growth_directions || [], sprawl_index: 3.0, raster_png_url: null,
  }
}

export function getMockGeoZones(cityId) {
  const { city } = getMockFullAnalysis(cityId)
  return { type: 'FeatureCollection', city_id: city.id, city_name: city.name, center: [city.lng, city.lat], features: [] }
}

// ── Investment scoring + copilot fallbacks ──────────────────────────────────
const _riskMock = (c) => {
  let s = { emerging: 70, accelerating: 52, maturing: 34, mature: 22 }[c.growth_phase] ?? 50
  if (c.tier === 3) s += 10
  if (c.dist_to_metro_km > 300) s += 8; else if (c.dist_to_metro_km > 120) s += 4
  if (!c.infrastructure?.has_airport) s += 5
  s = Math.max(5, Math.min(s, 95))
  return [s, s >= 62 ? 'high' : s >= 40 ? 'medium' : 'low']
}
const _roiMock = (c) => Math.round(Math.min(({ emerging: 0.115, accelerating: 0.09, maturing: 0.065, mature: 0.045 }[c.growth_phase] ?? 0.08) / 0.15 * 100, 100) * 10) / 10

export function getMockScore(cityId) {
  const c = MOCK_CITIES.find(x => x.id === cityId) || MOCK_CITIES[0]
  const [risk, level] = _riskMock(c)
  const roi = _roiMock(c)
  const demand = Math.round(Math.min((c.population['2021'] / Math.max(c.population['2001'], 1) - 1) * 60, 45) + c.scores.economic_activity * 0.35 + (c.government_schemes || []).length * 4)
  const fdp = Math.min(30 + (c.growth_triggers || []).length * 7 + ({ emerging: 22, accelerating: 16, maturing: 6, mature: 0 }[c.growth_phase] ?? 8), 100)
  const composite = Math.round(roi * 0.26 + demand * 0.18 + fdp * 0.16 + c.scores.infrastructure * 0.12 + c.scores.connectivity * 0.10 + c.scores.economic_activity * 0.10 + (100 - risk) * 0.08)
  return {
    city_id: c.id, city_name: c.name, composite_score: composite, headline_investment_score: c.investment_score,
    sub_scores: { roi_score: roi, risk_score: risk, risk_level: level, liquidity_score: Math.min(60 + { 1: 30, 2: 20, 3: 10 }[c.tier], 100), demand_score: demand, future_development_probability: fdp, infrastructure_score: c.scores.infrastructure, connectivity_score: c.scores.connectivity, economic_score: c.scores.economic_activity },
    rationale: {
      strengths: [c.infrastructure?.has_airport ? 'Airport access widens the catchment.' : 'Rail + road connectivity supports growth.', c.growth_phase === 'emerging' ? 'Early-stage market — most upside.' : `Strong fundamentals (score ${c.investment_score}).`],
      watch_outs: [level === 'high' ? 'High-risk early/peripheral market — verify infra execution.' : 'Standard market risks apply.'],
    },
    model_drivers: null, recommendation: composite >= 75 && level !== 'high' ? 'Buy Now' : composite >= 62 ? 'Buy Early' : composite >= 48 ? 'Watch' : 'Hold',
  }
}

export function getMockCopilot(q, top = 6) {
  const ql = (q || '').toLowerCase()
  let list = MOCK_CITIES.slice()
  const intent = {}
  const mp = ql.match(/([\d,]+)\s*(?:\/|per\s?)?\s?sq/); if (mp) { intent.max_price_per_sqft = +mp[1].replace(/,/g, '') }
  const mb = ql.match(/([\d.]+)\s*(lakhs?|crores?|cr)/); if (mb && !intent.max_price_per_sqft) { const l = mb[2].startsWith('cr') ? +mb[1] * 100 : +mb[1]; intent.budget_lakh = l; intent.max_price_per_sqft = Math.round(l * 100) }
  const mt = ql.match(/tier[- ]?([123])/); if (mt) intent.tier = +mt[1];
  ['emerging', 'accelerating', 'maturing', 'mature'].forEach(p => { if (ql.includes(p)) intent.phase = p })
  MOCK_STATES.forEach(s => { if (ql.includes(s.toLowerCase())) intent.state = s })
  if (/low[- ]?risk|safe|stable/.test(ql)) intent.risk = 'low'
  if (/high[- ]?growth|aggressive|roi|appreciation|return|upside/.test(ql)) intent.sort = 'roi'
  if (/near (a )?metro|close to (a )?metro/.test(ql)) intent.near_metro = true
  if (intent.state) list = list.filter(c => c.state === intent.state)
  if (intent.tier) list = list.filter(c => c.tier === intent.tier)
  if (intent.phase) list = list.filter(c => c.growth_phase === intent.phase)
  if (intent.max_price_per_sqft) list = list.filter(c => c.land_price_inr_per_sqft['2021'] <= intent.max_price_per_sqft)
  if (intent.near_metro) list = list.filter(c => c.dist_to_metro_km <= 120)
  if (intent.risk === 'low') list = list.filter(c => _riskMock(c)[0] < 62)
  let sortBy = 'investment score'
  if (intent.sort === 'roi') { list.sort((a, b) => _roiMock(b) - _roiMock(a)); sortBy = 'modelled ROI' }
  else if (intent.risk === 'low') { list.sort((a, b) => _riskMock(a)[0] - _riskMock(b)[0]); sortBy = 'lowest risk' }
  else if (intent.max_price_per_sqft) { list.sort((a, b) => a.land_price_inr_per_sqft['2021'] - b.land_price_inr_per_sqft['2021']); sortBy = 'affordability' }
  else list.sort((a, b) => b.investment_score - a.investment_score)
  const results = list.slice(0, top).map(c => ({ city_id: c.id, name: c.name, state: c.state, tier: c.tier, growth_phase: c.growth_phase, investment_score: c.investment_score, land_price_2021: c.land_price_inr_per_sqft['2021'], roi_score: _roiMock(c), risk_level: _riskMock(c)[1], dist_to_metro_km: c.dist_to_metro_km, reason: `score ${c.investment_score} · ${c.growth_phase}` }))
  return { query: q, interpretation: intent, summary: `Showing ${results.length} cities, ranked by ${sortBy}.`, sort_by: sortBy, count: results.length, results }
}
"""

header = (
    "// ─── LandAI Mock Data (AUTO-GENERATED from the FastAPI backend) ─────────────\n"
    "// Fallback dataset used when the backend is offline. Mirrors /api/cities so the\n"
    "// UI shows identical numbers whether the backend is up or not.\n"
    f"// {len(cities)} cities across {len(states)} states. Regenerate: python scripts/generate_mock_data.py\n\n"
)

out = header
out += f"export const MOCK_STATES = {json.dumps(states, ensure_ascii=False)}\n\n"
out += f"export const MOCK_CITIES = {json.dumps(cities, indent=0, ensure_ascii=False)}\n"
out += HELPERS

with open(OUT, "w") as f:
    f.write(out)

print(f"Wrote {OUT}: {len(cities)} cities, {len(states)} states, {len(out)} bytes")
