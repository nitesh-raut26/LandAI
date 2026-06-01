// Watchlist with graceful persistence: localStorage is always the instant
// source of truth (works logged-out / offline); when a user is signed in we
// sync to the server so the list follows them across devices.
//
// Sync is additive (union) on load — a deliberate, honest simplification:
// logging in merges your local list with the server's rather than doing true
// last-write-wins reconciliation. Writes (toggle) are mirrored best-effort.
import { useState, useEffect } from 'react'
import { getAuthToken, listWatchlist, addWatchApi, removeWatchApi } from './api'

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
  // Best-effort server mirror — never blocks the UI, never throws.
  if (getAuthToken()) {
    (ids.includes(id) ? removeWatchApi(id) : addWatchApi(id)).catch(() => {})
  }
  return next
}

// One-time merge of the server watchlist into the local one (on sign-in / load).
async function mergeFromServer() {
  if (!getAuthToken()) return read()
  try {
    const server = (await listWatchlist()).map(w => w.city_id)
    const local = read()
    const merged = Array.from(new Set([...local, ...server]))
    // Push any local-only ids up so the server reflects the merged set.
    server.length || local.length
      ? local.filter(id => !server.includes(id)).forEach(id => addWatchApi(id).catch(() => {}))
      : null
    write(merged)
    return merged
  } catch {
    return read()  // server unreachable → stay local-only (honest degradation)
  }
}

// React hook — re-renders on any watchlist change (this tab or another), and
// hydrates from the server once when signed in.
export function useWatchlist() {
  const [ids, setIds] = useState(read())
  useEffect(() => {
    const sync = () => setIds(read())
    window.addEventListener('watchlist-change', sync)
    window.addEventListener('storage', sync)
    mergeFromServer().then(setIds)
    return () => {
      window.removeEventListener('watchlist-change', sync)
      window.removeEventListener('storage', sync)
    }
  }, [])
  return { ids, toggle: toggleWatch, isWatched: (id) => ids.includes(id) }
}
