import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { fetchMe, getAuthToken, loginUser, logoutAllApi, logoutUser, registerUser, setAuthToken } from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadMe = useCallback(async () => {
    if (!getAuthToken()) { setUser(null); setLoading(false); return }
    try {
      setUser(await fetchMe())
    } catch {
      setAuthToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadMe() }, [loadMe])

  const _afterToken = async (tokens) => {
    setAuthToken(tokens.access_token)
    try { localStorage.setItem('landai_refresh', tokens.refresh_token) } catch { /* ignore */ }
    setUser(await fetchMe())
  }

  const login = async (email, password) => { await _afterToken(await loginUser(email, password)) }
  const register = async (email, password) => { await _afterToken(await registerUser(email, password)) }
  const _clearLocal = () => {
    setAuthToken(null)
    try { localStorage.removeItem('landai_refresh') } catch { /* ignore */ }
    setUser(null)
  }
  const logout = async () => {
    try { await logoutUser() } catch { /* ignore */ }
    _clearLocal()
  }
  const logoutAll = async () => {
    try { await logoutAllApi() } catch { /* ignore */ }
    _clearLocal()
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, logoutAll, reload: loadMe }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext) || { user: null, loading: false }
