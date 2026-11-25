// Giriş ekranı (sorumlu: Berat). Rota: /login
// Yanlış e-posta/parola (401) için mesaj bu sayfada verilir; api.js genel mesaj üretir.

import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const redirectTo = location.state?.from ?? '/'
  const sessionExpired = Boolean(location.state?.sessionExpired)

  const [form, setForm] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [saving, setSaving] = useState(false)

  if (isAuthenticated) return <Navigate to={redirectTo} replace />

  const update = (field) => (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }))

  async function handleSubmit(event) {
    event.preventDefault()
    const found = {}
    if (!form.email.trim()) found.email = 'E-posta adresini yaz.'
    if (!form.password) found.password = 'Parolanı yaz.'
    setErrors(found)
    setSubmitError('')
    if (Object.keys(found).length > 0) {
      document.getElementById(found.email ? 'email' : 'password')?.focus()
      return
    }

    setSaving(true)
    try {
      await login({ email: form.email, password: form.password })
      navigate(redirectTo, { replace: true })
    } catch (error) {
      setSubmitError(
        error.status === 401 || error.status === 422
          ? 'E-posta veya parola hatalı.'
          : error.message,
      )
      setForm((prev) => ({ ...prev, password: '' }))
      document.getElementById('password')?.focus()
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="container container-narrow">
      <section className="card">
        <h1>Giriş yap</h1>

        {sessionExpired && !submitError && (
          <div className="alert alert-info" role="status">
            Oturumunun süresi doldu. Devam etmek için tekrar giriş yap.
          </div>
        )}

        {submitError && (
          <div className="alert alert-error" role="alert">
            {submitError}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="email">E-posta</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              maxLength={254}
              value={form.email}
              onChange={update('email')}
              aria-invalid={errors.email ? 'true' : 'false'}
              aria-describedby={errors.email ? 'email-error' : undefined}
            />
            {errors.email && (
              <span id="email-error" className="field-error">
                {errors.email}
              </span>
            )}
          </div>
          <div className="field">
            <label htmlFor="password">Parola</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              maxLength={128}
              value={form.password}
              onChange={update('password')}
              aria-invalid={errors.password ? 'true' : 'false'}
              aria-describedby={errors.password ? 'password-error' : undefined}
            />
            {errors.password && (
              <span id="password-error" className="field-error">
                {errors.password}
              </span>
            )}
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
            {saving ? 'Giriş yapılıyor…' : 'Giriş yap'}
          </button>
        </form>

        <p className="form-footer">
          Hesabın yok mu? <Link to="/register">Kayıt ol</Link>
        </p>
      </section>
    </main>
  )
}
