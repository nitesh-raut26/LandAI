import { useEffect, useRef } from 'react'
import L from 'leaflet'
import { scoreColor } from '../utils/api'

export default function GrowthZoneMap({ city, zones = [], height = 380 }) {
  const mapRef = useRef(null)
  const mapInstanceRef = useRef(null)

  useEffect(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove()
      mapInstanceRef.current = null
    }
    if (!city || !mapRef.current) return

    const map = L.map(mapRef.current, {
      center: [city.lat, city.lng],
      zoom: 11,
      zoomControl: true,
      attributionControl: false
    })

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 18, opacity: 0.92
    }).addTo(map)

    const currentArea = city.urban_area_sqkm?.['2021'] || 10
    const rCurrent = Math.sqrt(currentArea / Math.PI) * 1000

    // Current boundary — indigo
    L.circle([city.lat, city.lng], {
      radius: rCurrent,
      color: '#4338CA', fillColor: '#4338CA',
      fillOpacity: 0.06, weight: 2
    }).bindTooltip('Current Urban Boundary (2021)').addTo(map)

    // 5-year ring — amber
    const r5extra = (zones.find(z => z.horizon_years === 5)?.radius_km || 2) * 1000
    L.circle([city.lat, city.lng], {
      radius: rCurrent + r5extra,
      color: '#D97706', fillColor: '#D97706',
      fillOpacity: 0.04, weight: 2, dashArray: '6 4'
    }).bindTooltip('Predicted Growth Zone — 2026').addTo(map)

    // 10-year ring — orange
    const r10extra = (zones.find(z => z.horizon_years === 10)?.radius_km || 3) * 1000
    L.circle([city.lat, city.lng], {
      radius: rCurrent + r5extra + r10extra,
      color: '#F97316', fillColor: '#F97316',
      fillOpacity: 0.03, weight: 2, dashArray: '4 6'
    }).bindTooltip('Predicted Growth Zone — 2031').addTo(map)

    // Zone markers
    zones.slice(0, 8).forEach(zone => {
      const sc = scoreColor(zone.investment_score)
      L.circleMarker([zone.center_lat, zone.center_lng], {
        radius: 9, color: sc, fillColor: sc, fillOpacity: 0.88, weight: 2
      }).bindPopup(`
        <div style="font-family:DM Sans,Inter,sans-serif;padding:4px">
          <div style="font-weight:700;font-size:14px;color:#111827;margin-bottom:6px">${zone.label}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
            <div><div style="font-size:10px;color:#9CA3AF;font-weight:500">Score</div><div style="font-weight:700;color:${sc}">${zone.investment_score}</div></div>
            <div><div style="font-size:10px;color:#9CA3AF;font-weight:500">Expected Rise</div><div style="font-weight:700;color:#059669">+${zone.expected_price_rise_pct}%</div></div>
          </div>
          <div style="background:rgba(67,56,202,0.08);border:1px solid rgba(67,56,202,0.2);padding:6px 10px;border-radius:8px;font-size:12.5px;font-weight:600;color:#4338CA;text-align:center">
            ${zone.recommendation}
          </div>
        </div>
      `, { maxWidth: 210 }).addTo(map)
    })

    // City pin
    L.marker([city.lat, city.lng], {
      icon: L.divIcon({
        html: `<div style="width:14px;height:14px;background:#F43F5E;border-radius:50%;border:3px solid #fff;box-shadow:0 0 10px rgba(244,63,94,0.5), 0 2px 6px rgba(0,0,0,0.15)"></div>`,
        className: '', iconSize: [14, 14], iconAnchor: [7, 7]
      })
    }).bindTooltip(`${city.name} City Centre`).addTo(map)

    mapInstanceRef.current = map

    return () => {
      map.remove()
      mapInstanceRef.current = null
    }
  }, [city, zones])

  return (
    <div style={{ position: 'relative' }}>
      <div ref={mapRef} style={{ height, width: '100%', borderRadius: 14, overflow: 'hidden', border: '1px solid var(--border-faint)' }} />
      <div style={{
        position: 'absolute', bottom: 14, left: 14, zIndex: 500,
        background: 'rgba(255, 255, 255, 0.92)', backdropFilter: 'blur(12px)',
        border: '1px solid rgba(17, 24, 39, 0.08)', borderRadius: 11,
        padding: '10px 14px', fontSize: 12.5,
        boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
      }}>
        {[
          { color: '#4338CA', label: 'Current boundary (2021)', dot: false },
          { color: '#D97706', label: '5-yr growth zone (2026)', dot: false },
          { color: '#F97316', label: '10-yr growth zone (2031)', dot: false },
          { color: '#059669', label: 'Investment zone marker', dot: true },
        ].map(item => (
          <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5, color: '#6B7280', fontWeight: 500 }}>
            {item.dot
              ? <div style={{ width: 10, height: 10, borderRadius: '50%', background: item.color, flexShrink: 0 }} />
              : <div style={{ width: 22, height: 2, background: item.color, flexShrink: 0, borderRadius: 1 }} />
            }
            {item.label}
          </div>
        ))}
      </div>
    </div>
  )
}
