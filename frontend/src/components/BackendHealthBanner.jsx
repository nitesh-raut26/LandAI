import { AnimatePresence, motion } from 'framer-motion'
import { AlertTriangle, Gauge, WifiOff } from 'lucide-react'
import { useDataTrust } from '../context/DataTrustContext'
import { timeAgo } from '../utils/trust'

/**
 * Global, honest degradation banner. Renders nothing when the backend is fully
 * healthy; slides in when the backend is unreachable (red) or degraded (amber).
 * This is what makes fallback NON-silent.
 */
export default function BackendHealthBanner() {
  const t = useDataTrust()
  const offline = t.backendOnline === false
  const rateLimited = !offline && t.rateLimited
  const degraded = !offline && !rateLimited && (t.degraded?.length > 0)
  const show = offline || rateLimited || degraded

  const cfg = offline
    ? {
        bg: 'rgba(239,68,68,0.10)', bd: 'rgba(239,68,68,0.30)', fg: '#B91C1C', Icon: WifiOff,
        msg: 'Backend unavailable — showing a curated offline snapshot. Figures are last-known, not live.',
      }
    : rateLimited
    ? {
        bg: 'rgba(59,130,246,0.10)', bd: 'rgba(59,130,246,0.30)', fg: '#1D4ED8', Icon: Gauge,
        msg: "You're sending requests quickly — briefly throttled to protect the service. Normal access resumes automatically.",
      }
    : {
        bg: 'rgba(245,158,11,0.12)', bd: 'rgba(245,158,11,0.32)', fg: '#B45309', Icon: AlertTriangle,
        msg: `Degraded mode: ${(t.degraded || []).join(' · ')}.`,
      }

  return (
    <AnimatePresence initial={false}>
      {show && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
          style={{ overflow: 'hidden', background: cfg.bg, borderBottom: `1px solid ${cfg.bd}` }}
        >
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '8px 20px', fontSize: 13, color: cfg.fg,
          }}>
            <cfg.Icon size={16} style={{ flexShrink: 0 }} />
            <span style={{ fontWeight: 600 }}>{cfg.msg}</span>
            {t.lastChecked && (
              <span style={{ marginLeft: 'auto', fontWeight: 500, opacity: 0.8, whiteSpace: 'nowrap' }}>
                checked {timeAgo(t.lastChecked)}
              </span>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
