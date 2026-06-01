import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Loader2, MapPinned, WifiOff } from 'lucide-react'
import { fetchLiveAmenities } from '../utils/api'
import ProvenanceStrip from './ProvenanceStrip'

const CAT_LABEL = {
  school: 'Schools', university: 'Universities', hospital: 'Hospitals', clinic: 'Clinics',
  mall: 'Malls', metro_station: 'Metro stations', railway_station: 'Railway stations',
  airport: 'Airports', industrial: 'Industrial zones', highway_access: 'Highway junctions',
}
const SCORE_LABEL = {
  amenity_density: 'Amenity density', accessibility: 'Accessibility', livability: 'Livability',
  education: 'Education', healthcare: 'Healthcare', retail: 'Retail',
}
const fmtKm = (v) => (v == null ? '—' : `${v} km`)

export default function LiveAmenities({ cityId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!cityId) return
    setLoading(true); setData(null)
    fetchLiveAmenities(cityId).then(setData).finally(() => setLoading(false))
  }, [cityId])

  if (loading) {
    return (
      <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, color: '#9CA3AF' }}>
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 0.9, ease: 'linear' }}>
          <Loader2 size={22} color="var(--teal)" />
        </motion.div>
        Querying OpenStreetMap…
      </div>
    )
  }

  if (!data || data.available === false) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, padding: '34px 20px', textAlign: 'center' }}>
        <WifiOff size={26} color="#D97706" />
        <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>
          Live OSM data unavailable
        </div>
        <div style={{ fontSize: 13, color: '#6B7280', maxWidth: 460, lineHeight: 1.6 }}>
          {(data?.source) || 'OpenStreetMap'} couldn't be reached right now
          {data?.reason ? ` (${data.reason})` : ''}. We do <strong>not</strong> substitute
          fabricated numbers — real amenity intelligence appears here once a global Overpass
          endpoint is reachable from the server.
        </div>
      </div>
    )
  }

  const am = data.amenities || {}
  const counts = am.counts_by_category || {}
  const scores = am.scores || {}
  const nearest = am.nearest_km || {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <MapPinned size={16} color="#059669" />
        <span style={{ fontWeight: 700, fontSize: 14.5, color: 'var(--text-primary)', fontFamily: 'DM Sans, sans-serif' }}>
          Live amenities within {am.radius_km} km
        </span>
        <span style={{ marginLeft: 'auto', fontSize: 12.5, color: '#6B7280', fontWeight: 600 }}>
          {am.total_amenities} mapped POIs
        </span>
      </div>

      {/* Real provenance: source · license · confidence · freshness · cache state */}
      <ProvenanceStrip provenance={data.provenance} kind="real_live" />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
        {Object.entries(scores).map(([k, v]) => (
          <div key={k} style={{ background: 'var(--bg-base)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 12px' }}>
            <div className="stat-label" style={{ marginBottom: 4 }}>{SCORE_LABEL[k] || k}</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: '#0D9488', fontFamily: 'DM Sans, sans-serif' }}>{v}</div>
          </div>
        ))}
      </div>

      <div>
        <div className="section-title" style={{ marginBottom: 10 }}>Mapped amenities by type</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([k, v]) => (
            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', background: 'var(--bg-card)', border: '1px solid var(--border-faint)', borderRadius: 9, padding: '8px 12px', fontSize: 13 }}>
              <span style={{ color: '#6B7280' }}>{CAT_LABEL[k] || k}</span>
              <strong style={{ color: 'var(--text-primary)' }}>{v}</strong>
            </div>
          ))}
        </div>
      </div>

      <div style={{ fontSize: 12.5, color: '#6B7280' }}>
        Nearest — metro: <strong>{fmtKm(nearest.metro_station)}</strong> · railway:{' '}
        <strong>{fmtKm(nearest.railway_station)}</strong> · airport: <strong>{fmtKm(nearest.airport)}</strong>
      </div>
    </div>
  )
}
