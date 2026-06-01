import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, MapPin, X } from 'lucide-react'
import { searchCities, tierColor, phaseColor } from '../utils/api'

export default function CitySearch({ placeholder = 'Search city or state...', onSelect, compact = false }) {
  const [query, setQuery]     = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen]       = useState(false)
  const [focused, setFocused] = useState(false)
  const wrapRef               = useRef(null)
  const navigate              = useNavigate()

  useEffect(() => {
    if (!query.trim()) { setResults([]); setOpen(false); return }
    setLoading(true)
    const t = setTimeout(async () => {
      try {
        const data = await searchCities({ q: query })
        setResults(data.slice(0, 8))
        setOpen(true)
      } catch {
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 200)
    return () => clearTimeout(t)
  }, [query])

  useEffect(() => {
    const h = (e) => { if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  const handleSelect = (city) => {
    setQuery(''); setOpen(false)
    if (onSelect) onSelect(city)
    else navigate(`/city/${city.id}`)
  }

  return (
    <div ref={wrapRef} style={{ position: 'relative', width: '100%' }}>
      {/* Input */}
      <div style={{ position: 'relative' }}>
        <Search
          size={16}
          style={{
            position: 'absolute', left: 14, top: '50%',
            transform: 'translateY(-50%)',
            color: focused ? 'var(--teal)' : '#9CA3AF',
            pointerEvents: 'none',
            transition: 'color 0.2s',
          }}
        />
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder={placeholder}
          onFocus={() => { setFocused(true); results.length && setOpen(true) }}
          onBlur={() => setFocused(false)}
          style={{
            paddingLeft: 42,
            paddingRight: query ? 38 : 16,
            height: compact ? 40 : 52,
            fontSize: compact ? 13.5 : 15,
            borderRadius: compact ? 11 : 14,
            boxShadow: focused
              ? '0 0 0 3px rgba(13,148,136,0.1), 0 4px 20px rgba(0,0,0,0.08)'
              : '0 2px 12px rgba(0,0,0,0.06)',
            border: `1.5px solid ${focused ? 'var(--teal)' : 'var(--border)'}`,
            transition: 'border-color 0.2s, box-shadow 0.2s',
          }}
        />
        {query && (
          <button
            onClick={() => { setQuery(''); setOpen(false) }}
            style={{
              position: 'absolute', right: 11, top: '50%', transform: 'translateY(-50%)',
              background: 'rgba(107,114,128,0.1)', border: 'none',
              color: '#6B7280', padding: 4, borderRadius: '50%',
              display: 'flex', alignItems: 'center',
              cursor: 'pointer',
            }}
          >
            <X size={12} />
          </button>
        )}
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.16, ease: [0.4, 0, 0.2, 1] }}
            style={{
              position: 'absolute', top: 'calc(100% + 8px)', left: 0, right: 0, zIndex: 9999,
              background: 'var(--bg-card)',
              border: '1.5px solid var(--border)',
              borderRadius: 14,
              boxShadow: '0 12px 48px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.06)',
              maxHeight: 360, overflowY: 'auto',
            }}
          >
            {loading && (
              <div style={{ padding: '16px 18px', color: '#9CA3AF', fontSize: 13.5, display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 14, height: 14, borderRadius: '50%',
                  border: '2px solid #E5E7EB', borderTopColor: 'var(--teal)',
                  animation: 'spin 0.7s linear infinite', flexShrink: 0,
                }} />
                Searching…
              </div>
            )}
            {!loading && results.length === 0 && (
              <div style={{ padding: '16px 18px', color: '#9CA3AF', fontSize: 13.5 }}>
                No cities found for "{query}"
              </div>
            )}
            {results.map((city, idx) => {
              const tc = tierColor(city.tier)
              const pc = phaseColor(city.growth_phase)
              return (
                <motion.button
                  key={city.id}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.035, duration: 0.2 }}
                  onClick={() => handleSelect(city)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 12,
                    width: '100%', padding: '11px 16px',
                    background: 'none', border: 'none',
                    textAlign: 'left', cursor: 'pointer',
                    borderBottom: idx < results.length - 1
                      ? '1px solid var(--border-faint)' : 'none',
                    transition: 'background 0.12s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-base)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'none'}
                >
                  <div style={{
                    width: 36, height: 36, borderRadius: 10, flexShrink: 0,
                    background: `${tc}10`, border: `1px solid ${tc}22`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <MapPin size={15} color={tc} strokeWidth={2} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: 14.5, color: 'var(--text-primary)', marginBottom: 2 }}>
                      {city.name}
                    </div>
                    <div style={{ fontSize: 12.5, color: '#9CA3AF', fontWeight: 500 }}>
                      {city.state} · Tier {city.tier}
                    </div>
                  </div>
                  <span style={{
                    fontSize: 11, fontWeight: 600, padding: '3px 10px', borderRadius: 100,
                    background: `${pc}10`, color: pc, border: `1px solid ${pc}20`,
                    textTransform: 'capitalize', flexShrink: 0,
                  }}>{city.growth_phase}</span>
                </motion.button>
              )
            })}
            <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
