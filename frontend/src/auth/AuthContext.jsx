// Oturum durumu (sorumlu: Berat). Giriş yapan kullanıcı bütün sayfalarda useAuth() ile okunur.
// Token api.js içinde bellekte tutulur; sayfa yenilenince oturum kapanır (ekip kararı).

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { setUnauthorizedHandler } from '../services/api.js'
import * as authApi from '../services/authApi.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()

  const login = useCallback(async (credentials) => {
    const me = await authApi.login(credentials)
    setUser(me)
    return me
  }, [])

  const logout = useCallback(() => {
    authApi.logout()
    setUser(null)
  }, [])

  // Oturumlu bir istek 401 alırsa (token süresi doldu vb.) çıkış yapıp giriş sayfasına yönlendir.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      authApi.logout()
      setUser(null)
      navigate('/login', { replace: true, state: { sessionExpired: true } })
    })
    return () => setUnauthorizedHandler(null)
  }, [navigate])

  const value = useMemo(
    () => ({ user, isAuthenticated: Boolean(user), login, logout }),
    [user, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// oxlint-disable-next-line react/only-export-components -- hook, bileşenle aynı dosyada
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth, AuthProvider içinde kullanılmalı.')
  return context
}
