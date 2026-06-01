import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Check } from 'lucide-react'

/**
 * CustomSelect — fully animated dropdown replacing <select>
 * Props:
 *   options: [{ value, label }]
 *   value: string
 *   onChange: (value) => void
 *   placeholder: string
 *   minWidth: number (optional)
 */
export default function CustomSelect({
  options = [],
  value,
  onChange,
  placeholder = 'Select…',
  minWidth = 120,
  style = {},
}) {
  const [open, setOpen] = useState(false)
  const wrapRef = useRef(null)

  const selected = options.find(o => o.value === value)

  useEffect(() => {
    const handler = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleKey = (e) => {
    if (e.key === 'Escape') setOpen(false)
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(v => !v) }
  }

  return (
    <div ref={wrapRef} className="cs-wrapper" style={{ minWidth, ...style }}>
      <button
        type="button"
        className={`cs-trigger ${open ? 'cs-open' : ''}`}
        onClick={() => setOpen(v => !v)}
        onKeyDown={handleKey}
        aria-haspopup="listbox"
        aria-expanded={open}
        style={{ minWidth }}
      >
        <span className="cs-trigger-text" style={{ color: selected ? 'var(--text-primary)' : 'var(--text-muted)' }}>
          {selected ? selected.label : placeholder}
        </span>
        <ChevronDown size={14} className="cs-chevron" />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="cs-panel"
            initial={{ opacity: 0, y: -6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.97 }}
            transition={{ duration: 0.16, ease: [0.4, 0, 0.2, 1] }}
            role="listbox"
          >
            {options.map((opt) => {
              const isSelected = opt.value === value
              return (
                <button
                  key={opt.value}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  className={`cs-option ${isSelected ? 'cs-selected' : ''}`}
                  onClick={() => {
                    onChange(opt.value)
                    setOpen(false)
                  }}
                >
                  <span className="cs-option-dot" />
                  {opt.label}
                  {isSelected && (
                    <Check size={13} style={{ marginLeft: 'auto', color: 'var(--teal)', flexShrink: 0 }} />
                  )}
                </button>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
