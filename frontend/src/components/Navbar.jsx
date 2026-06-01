import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, BarChart2, GitCompare, TrendingUp, Menu, X, PieChart } from 'lucide-react'
import { fetchAllCities } from '../utils/api'
import DataStatusBadge from './DataStatusBadge'

const NAV_LINKS = [
  { to: '/',          label: 'Explore Map', icon: MapPin     },
  { to: '/analytics', label: 'Analytics',   icon: PieChart   },
  { to: '/city',      label: 'Analysis',    icon: BarChart2  },
  { to: '/compare',   label: 'Compare',     icon: GitCompare },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const [open, setOpen] = useState(false)
  const [cityCount, setCityCount] = useState(null)

  useEffect(() => {
    let alive = true
    fetchAllCities()
      .then(c => { if (alive) setCityCount(Array.isArray(c) ? c.length : null) })
      .catch(() => {})
    return () => { alive = false }
  }, [])

  const isActive = (to) =>
    to === '/' ? pathname === '/' : pathname.startsWith(to)

  return (
    <>
      <motion.nav
        initial={{ y: -10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        style={{
          background: 'rgba(255, 255, 255, 0.88)',
          borderBottom: '1px solid rgba(17, 24, 39, 0.08)',
          backdropFilter: 'blur(28px)',
          WebkitBackdropFilter: 'blur(28px)',
          position: 'sticky', top: 0, zIndex: 1000,
          height: 66,
          display: 'flex', alignItems: 'center',
          padding: '0 28px',
          justifyContent: 'space-between',
          gap: 16,
        }}
      >
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 11, flexShrink: 0 }}>
          <motion.div
            whileHover={{ scale: 1.06, rotate: -3 }}
            transition={{ type: 'spring', stiffness: 400, damping: 17 }}
            style={{
              width: 38, height: 38, borderRadius: 12, flexShrink: 0,
              background: 'linear-gradient(135deg, #4338CA 0%, #0D9488 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 16px rgba(67, 56, 202, 0.28)',
            }}
          >
            <TrendingUp size={18} color="#fff" strokeWidth={2.5} />
          </motion.div>
          <div>
            <div style={{
              fontFamily: 'DM Sans, Inter, sans-serif',
              fontWeight: 800, fontSize: 18, color: '#111827',
              letterSpacing: '-0.5px', lineHeight: 1.1,
            }}>
              Land<span style={{
                background: 'linear-gradient(135deg, #4338CA, #0D9488)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>AI</span>
            </div>
            <div style={{ fontSize: 10, color: '#9CA3AF', marginTop: 1, letterSpacing: '0.2px', fontWeight: 500 }}>
              India Urban Intelligence
            </div>
          </div>
        </Link>

        {/* Desktop links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 2 }} className="nav-links">
          {NAV_LINKS.map(({ to, label, icon: Icon }) => {
            const active = isActive(to)
            return (
              <Link key={to} to={to} style={{
                display: 'flex', alignItems: 'center', gap: 7,
                padding: '7px 15px', borderRadius: 10,
                fontSize: 14, fontWeight: active ? 600 : 500,
                color: active ? '#4338CA' : '#6B7280',
                background: active ? 'rgba(67, 56, 202, 0.08)' : 'transparent',
                border: `1px solid ${active ? 'rgba(67, 56, 202, 0.2)' : 'transparent'}`,
                transition: 'all 0.15s ease',
                position: 'relative',
              }}
              onMouseEnter={e => {
                if (!active) {
                  e.currentTarget.style.color = '#374151'
                  e.currentTarget.style.background = 'rgba(17, 24, 39, 0.04)'
                }
              }}
              onMouseLeave={e => {
                if (!active) {
                  e.currentTarget.style.color = '#6B7280'
                  e.currentTarget.style.background = 'transparent'
                }
              }}
              >
                <Icon size={15} strokeWidth={active ? 2.2 : 1.8} />
                {label}
              </Link>
            )
          })}
        </div>

        {/* Right side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }} className="nav-status">
            {cityCount != null && (
              <span style={{ fontSize: 12.5, color: 'var(--text-muted)', fontWeight: 500 }}>
                {cityCount} cities
              </span>
            )}
            <DataStatusBadge kind="curated" compact />
          </div>

          {/* Mobile burger */}
          <motion.button
            onClick={() => setOpen(v => !v)}
            whileTap={{ scale: 0.94 }}
            className="nav-burger"
            style={{
              background: 'var(--bg-card)', border: '1.5px solid var(--border)',
              borderRadius: 9, padding: '6px 8px',
              color: '#6B7280', display: 'none', alignItems: 'center',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            {open ? <X size={18} /> : <Menu size={18} />}
          </motion.button>
        </div>
      </motion.nav>

      {/* Mobile drawer */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.18, ease: [0.4, 0, 0.2, 1] }}
            style={{
              position: 'fixed', top: 66, left: 0, right: 0, zIndex: 999,
              background: 'rgba(255, 255, 255, 0.97)',
              borderBottom: '1px solid var(--border-faint)',
              padding: '12px 16px 18px',
              backdropFilter: 'blur(24px)',
              boxShadow: 'var(--shadow-lg)',
            }}
          >
            {NAV_LINKS.map(({ to, label, icon: Icon }) => {
              const active = isActive(to)
              return (
                <Link key={to} to={to} onClick={() => setOpen(false)} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '12px 14px', borderRadius: 11, marginBottom: 4,
                  color: active ? '#4338CA' : '#6B7280',
                  background: active ? 'rgba(67, 56, 202, 0.07)' : 'transparent',
                  fontSize: 15, fontWeight: active ? 600 : 400,
                }}>
                  <Icon size={17} />
                  {label}
                </Link>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @media (max-width: 640px) {
          .nav-links  { display: none !important; }
          .nav-status { display: none !important; }
          .nav-burger { display: flex !important; }
        }
      `}</style>
    </>
  )
}
