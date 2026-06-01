import { createContext, useContext, useEffect, useState } from 'react'
import { fetchSystemHealth, subscribeApiEvents } from '../utils/api'

const DataTrustContext = createContext(null)
const POLL_MS = 20000

const INITIAL = {
  status: 'checking',     // 'online' | 'degraded' | 'offline' | 'checking'
  backendOnline: null,    // null until first check
  health: null,
  degraded: [],
  fallbackActive: false,  // an API call has fallen back to the curated mirror
  rateLimited: false,     // an API call was throttled (HTTP 429)
  lastChecked: null,
}

export function DataTrustProvider({ children }) {
  const [state, setState] = useState(INITIAL)

  useEffect(() => {
    let alive = true

    const check = async () => {
      try {
        const h = await fetchSystemHealth()
        if (!alive) return
        setState((s) => ({
          ...s,
          backendOnline: true,
          status: h.degraded_systems && h.degraded_systems.length ? 'degraded' : 'online',
          health: h,
          degraded: h.degraded_systems || [],
          fallbackActive: false,
          lastChecked: new Date().toISOString(),
        }))
      } catch (err) {
        if (!alive) return
        // Distinguish "unreachable" (network error, no response) from "reachable
        // but health route failed" — only the former is a true offline state.
        const reachable = !!(err && err.response)
        setState((s) => ({
          ...s,
          backendOnline: reachable,
          status: reachable ? 'degraded' : 'offline',
          degraded: reachable ? ['system health endpoint unavailable'] : [],
          fallbackActive: !reachable,
          lastChecked: new Date().toISOString(),
        }))
      }
    }

    let rlTimer
    check()
    const id = setInterval(check, POLL_MS)
    // React immediately to API-level events (don't wait for the next poll).
    const unsub = subscribeApiEvents((evt) => {
      if (!alive) return
      if (evt.type === 'offline') {
        setState((s) => (s.backendOnline === false ? s
          : { ...s, backendOnline: false, status: 'offline', fallbackActive: true }))
      } else if (evt.type === 'ratelimited') {
        setState((s) => ({ ...s, rateLimited: true }))
        clearTimeout(rlTimer)
        rlTimer = setTimeout(
          () => { if (alive) setState((s) => ({ ...s, rateLimited: false })) },
          Math.min(Math.max(evt.retryAfter || 5, 3), 60) * 1000,
        )
      }
    })

    return () => { alive = false; clearInterval(id); clearTimeout(rlTimer); unsub() }
  }, [])

  return <DataTrustContext.Provider value={state}>{children}</DataTrustContext.Provider>
}

export function useDataTrust() {
  return useContext(DataTrustContext) || INITIAL
}
