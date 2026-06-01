import { motion } from 'framer-motion'
import { TrendingUp } from 'lucide-react'

/** Centered card layout for the Login / Register pages (mobile-friendly). */
export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div style={{
      minHeight: 'calc(100vh - 66px)', display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '32px 16px', background: 'var(--bg-base)',
    }}>
      <motion.div
        initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        style={{
          width: '100%', maxWidth: 430, background: 'var(--bg-card)', border: '1px solid var(--border)',
          borderRadius: 18, padding: '28px 24px', boxShadow: 'var(--shadow-lg)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 11, marginBottom: 20 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 11, flexShrink: 0,
            background: 'linear-gradient(135deg,#4338CA,#0D9488)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <TrendingUp size={19} color="#fff" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 19, fontFamily: 'DM Sans, sans-serif', color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
              {title}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{subtitle}</div>
          </div>
        </div>
        {children}
        {footer && (
          <div style={{ marginTop: 18, fontSize: 13, color: 'var(--text-muted)', textAlign: 'center' }}>{footer}</div>
        )}
      </motion.div>
    </div>
  )
}

export const inputStyle = {
  width: '100%', padding: '11px 13px', borderRadius: 10, border: '1px solid var(--border)',
  fontSize: 14, fontFamily: 'inherit', background: 'var(--bg-card)', color: 'var(--text-primary)',
  outline: 'none', marginTop: 6,
}
export const labelStyle = { fontSize: 12.5, fontWeight: 600, color: 'var(--text-secondary)' }
