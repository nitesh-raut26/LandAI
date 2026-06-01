// Lightweight client-side watchlist (localStorage) — no auth/DB required.
import { useState, useEffect } from 'react'

const KEY = 'landai_watchlist'

const read = () => {
  try { return JSON.parse(localStorage.getItem(KEY)) || [] } catch { return [] }
}
const write = (ids) => {
  localStorage.setItem(KEY, JSON.stringify(ids))
  window.dispatchEvent(new Event('watchlist-change'))
}

export const getWatchlist = () => read()
export const isWatched = (id) => read().includes(id)
export const toggleWatch = (id) => {
  const ids = read()
  const next = ids.includes(id) ? ids.filter(x => x !== id) : [...ids, id]
  write(next)
  return next
}

// React hook — re-renders on any watchlist change (this tab or another)
export function useWatchlist() {
  const [ids, setIds] = useState(read())
  useEffect(() => {
    const sync = () => setIds(read())
    window.addEventListener('watchlist-change', sync)
    window.addEventListener('storage', sync)
    return () => {
      window.removeEventListener('watchlist-change', sync)
      window.removeEventListener('storage', sync)
    }
  }, [])
  return { ids, toggle: toggleWatch, isWatched: (id) => ids.includes(id) }
}
