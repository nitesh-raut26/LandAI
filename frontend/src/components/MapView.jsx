import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import L from 'leaflet'
import { tierColor, phaseColor } from '../utils/api'

const INDIA_CENTER = [22.5, 82.0]

function createCityIcon(tier) {
  const color = tierColor(tier)
  const size = tier === 1 ? 14 : tier === 2 ? 11 : 9
  const glowSize = tier === 1 ? 12 : tier === 2 ? 8 : 5
  return L.divIcon({
    html: `<div style="width:${size*2}px;height:${size*2}px;border-radius:50%;background:${color};opacity:0.92;border:2px solid rgba(255,255,255,0.9);box-shadow:0 0 ${glowSize}px ${color}80, 0 2px 6px rgba(0,0,0,0.15)"></div>`,
    className: '',
    iconSize: [size * 2, size * 2],
    iconAnchor: [size, size]
  })
}

export default function MapView({ cities = [], selectedId = null, height = 520 }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const markersRef = useRef([])
  const [heat, setHeat] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (mapInstanceRef.current || !mapRef.current) return

    const map = L.map(mapRef.current, {
      center: INDIA_CENTER,
      zoom: 5,
      zoomControl: true,
      attributionControl: false
    })

    // Light map tiles — Carto light
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 18,
      opacity: 0.92
    }).addTo(map)

    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map || !cities.length) return

    markersRef.current.forEach(m => m.remove())
    markersRef.current = []

    cities.forEach(city => {
      const sc = city.investment_score >= 75 ? '#059669' : city.investment_score >= 55 ? '#4338CA' : '#D97706'
      const marker = heat
        ? L.circleMarker([city.lat, city.lng], {
            radius: 7 + (city.investment_score / 100) * 16,
            color: sc, fillColor: sc, fillOpacity: 0.42, weight: 1, opacity: 0.75,
          })
        : L.marker([city.lat, city.lng], { icon: createCityIcon(city.tier) })

      marker.bindPopup(`
        <div style="font-family:DM Sans,Inter,sans-serif;min-width:220px;padding:4px">
          <div style="font-weight:800;font-size:16px;margin-bottom:7px;color:#111827;letter-spacing:-0.3px">${city.name}</div>
          <div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">
            <span style="background:#F9FAFB;border:1px solid #E5E7EB;padding:2px 9px;border-radius:100px;font-size:11.5px;color:#6B7280;font-weight:500">${city.state}</span>
            <span style="background:${tierColor(city.tier)}12;border:1px solid ${tierColor(city.tier)}25;padding:2px 9px;border-radius:100px;font-size:11.5px;color:${tierColor(city.tier)};font-weight:600">Tier ${city.tier}</span>
            <span style="background:${phaseColor(city.growth_phase)}12;border:1px solid ${phaseColor(city.growth_phase)}25;padding:2px 9px;border-radius:100px;font-size:11.5px;color:${phaseColor(city.growth_phase)};font-weight:600;text-transform:capitalize">${city.growth_phase}</span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
            <div>
              <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.4px;font-weight:500;margin-bottom:2px">Population</div>
              <div style="font-weight:700;font-size:14px;color:#111827">${(city.population['2021'] / 1e6).toFixed(2)}M</div>
            </div>
            <div>
              <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.4px;font-weight:500;margin-bottom:2px">Land Price</div>
              <div style="font-weight:700;font-size:14px;color:#111827">₹${city.land_price_inr_per_sqft['2021'].toLocaleString()}/sqft</div>
            </div>
          </div>
          <div style="margin-bottom:12px">
            <div style="font-size:10px;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.4px;font-weight:500;margin-bottom:5px">Investment Score</div>
            <div style="display:flex;align-items:center;gap:10px">
              <div style="flex:1;height:6px;background:#F3F4F6;border-radius:100px;overflow:hidden">
                <div style="width:${city.investment_score}%;height:100%;background:linear-gradient(90deg,${sc}80,${sc});border-radius:100px"></div>
              </div>
              <span style="font-weight:800;font-size:15px;color:${sc}">${city.investment_score}</span>
            </div>
          </div>
          <button
            onclick="(function(){window.__landai_nav('${city.id}')})()"
            style="width:100%;padding:9px;background:linear-gradient(135deg,#4338CA,#0D9488);color:#fff;border:none;border-radius:9px;font-size:13.5px;font-weight:600;cursor:pointer;font-family:DM Sans,sans-serif;letter-spacing:-0.2px">
            View Full Analysis →
          </button>
        </div>
      `, { maxWidth: 270 })

      marker.addTo(map)
      markersRef.current.push(marker)

      if (city.id === selectedId) {
        marker.openPopup()
        map.setView([city.lat, city.lng], 10)
      }
    })

    window.__landai_nav = (id) => navigate(`/city/${id}`)
  }, [cities, selectedId, navigate, heat])

  return (
    <div style={{
      position: 'relative', borderRadius: 18, overflow: 'hidden',
      border: '1px solid var(--border-faint)',
      boxShadow: 'var(--shadow-md)',
    }}>
      <div ref={mapRef} style={{ height, width: '100%' }} />

      {/* Heatmap toggle */}
      <button
        onClick={() => setHeat(h => !h)}
        style={{
          position: 'absolute', top: 14, right: 14, zIndex: 500,
          display: 'flex', alignItems: 'center', gap: 7,
          background: heat ? 'linear-gradient(135deg,#4338CA,#0D9488)' : 'rgba(255,255,255,0.94)',
          color: heat ? '#fff' : '#374151',
          border: heat ? 'none' : '1px solid rgba(17,24,39,0.1)',
          backdropFilter: 'blur(12px)', borderRadius: 10, padding: '8px 13px',
          fontSize: 12.5, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
        }}
      >
        <span style={{ width: 9, height: 9, borderRadius: '50%', background: heat ? '#fff' : '#F43F5E', boxShadow: heat ? 'none' : '0 0 6px #F43F5E' }} />
        {heat ? 'Score Heatmap: ON' : 'Score Heatmap'}
      </button>

      {/* Tier legend */}
      <div style={{
        position: 'absolute', bottom: 16, left: 16, zIndex: 500,
        background: 'rgba(255, 255, 255, 0.92)', backdropFilter: 'blur(12px)',
        border: '1px solid rgba(17, 24, 39, 0.08)', borderRadius: 12, padding: '11px 15px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
      }}>
        <div style={{ fontSize: 10, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.6px', fontWeight: 600, marginBottom: 9 }}>City Tier</div>
        {[
          { tier: 1, label: 'Tier 1 — Metro', size: 14 },
          { tier: 2, label: 'Tier 2 — Growing', size: 11 },
          { tier: 3, label: 'Tier 3 — Emerging', size: 9 },
        ].map(({ tier, label, size }) => (
          <div key={tier} style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 5, fontSize: 12.5, color: '#6B7280', fontWeight: 500 }}>
            <div style={{
              width: size, height: size, borderRadius: '50%',
              background: tierColor(tier), flexShrink: 0,
              boxShadow: `0 0 6px ${tierColor(tier)}60`,
            }} />
            {label}
          </div>
        ))}
      </div>

      {/* Phase legend */}
      <div style={{
        position: 'absolute', bottom: 16, right: 16, zIndex: 500,
        background: 'rgba(255, 255, 255, 0.92)', backdropFilter: 'blur(12px)',
        border: '1px solid rgba(17, 24, 39, 0.08)', borderRadius: 12, padding: '11px 15px',
        boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
      }}>
        <div style={{ fontSize: 10, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.6px', fontWeight: 600, marginBottom: 9 }}>Growth Phase</div>
        {['emerging', 'accelerating', 'maturing', 'mature'].map(ph => (
          <div key={ph} style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 5, fontSize: 12.5, color: '#6B7280', fontWeight: 500 }}>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: phaseColor(ph),
              boxShadow: `0 0 5px ${phaseColor(ph)}70`,
            }} />
            <span style={{ textTransform: 'capitalize' }}>{ph}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
