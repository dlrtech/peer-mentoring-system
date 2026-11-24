// Kayıt ekranı (sorumlu: Berat). Rota: /register
// Kurallar (ekip planı): ad 2–100, e-posta geçerli ve en fazla 254, parola 8–128 karakter.
// Yeni hesap doğrulanmamış (is_verified=false) oluşur; bu durum kullanıcıya açıkça söylenir.

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { register } from '../services/authApi.js'

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate({ fullName, email, password, passwordAgain }) {
  const errors = {}
  const name = fullName.trim()
  const mail = email.trim()
  if (name.length < 2) errors.fullName = 'Ad soyad en az 2 karakter olmalı.'
  else if (name.length > 100) errors.fullName = 'Ad soyad en fazla 100 karakter olabilir.'
  if (!mail) errors.email = 'E-posta adresini yaz.'
  else if (mail.length > 254 || !EMAIL_PATTERN.test(mail))
    errors.email = 'Geçerli bir e-posta adresi yaz (ör. ad@ornek.edu.tr).'
  if (password.length < 8) errors.password = 'Parola en az 8 karakter olmalı.'
  else if (password.length > 128) errors.password = 'Parola en fazla 128 karakter olabilir.'
  if (passwordAgain !== password) errors.passwordAgain = 'Parolalar aynı değil.'
  return errors
}

// Backend'in 422 alan adlarını formdaki alanlara ve Türkçe mesajlara çevirir.
const SERVER_FIELD_MESSAGES = {
  full_name: ['fullName', 'Ad soyad 2–100 karakter olmalı.'],
  email: ['email', 'Geçerli bir e-posta adresi yaz.'],
  password: ['password', 'Parola 8–128 karakter olmalı.'],
}

const FIELD_ORDER = ['fullName', 'email', 'password', 'passwordAgain']

function focusFirstError(errors) {
  const first = FIELD_ORDER.find((field) => errors[field])
  if (first) document.getElementById(first)?.focus()
}

function Field({ id, label, error, hint, ...inputProps }) {
  const describedBy = [hint && `${id}-hint`, error && `${id}-error`].filter(Boolean).join(' ')
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={describedBy || undefined}
        {...inputProps}
      />
      {hint && (
        <span id={`${id}-hint`} className="field-hint">
          {hint}
        </span>
      )}
      {error && (
        <span id={`${id}-error`} className="field-error">
          {error}
        </span>
      )}
    </div>
  )
}

export default function Register() {
  const [form, setForm] = useState({ fullName: '', email: '', password: '', passwordAgain: '' })
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [saving, setSaving] = useState(false)
  const [createdUser, setCreatedUser] = useState(null)

  const update = (field) => (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }))

  async function handleSubmit(event) {
    event.preventDefault()
    const found = validate(form)
    setErrors(found)
    setSubmitError('')
    if (Object.keys(found).length > 0) {
      focusFirstError(found)
      return
    }

    setSaving(true)
    try {
      const user = await register({
        fullName: form.fullName.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      setCreatedUser(user)
    } catch (error) {
      if (error.status === 409) {
        const emailError = { email: 'Bu e-posta ile zaten bir hesap var. Giriş yapmayı dene.' }
        setErrors(emailError)
        focusFirstError(emailError)
      } else if (error.status === 422) {
        const serverErrors = {}
        for (const key of Object.keys(error.fieldErrors)) {
          const mapped = SERVER_FIELD_MESSAGES[key]
          if (mapped) serverErrors[mapped[0]] = mapped[1]
        }
        setErrors(serverErrors)
        setSubmitError(error.message)
        focusFirstError(serverErrors)
      } else {
        setSubmitError(error.message)
      }
    } finally {
      setSaving(false)
    }
  }

  if (createdUser) {
    return (
      <main className="container container-narrow">
        <section className="card" aria-labelledby="register-done">
          <h1 id="register-done">Kaydın alındı</h1>
          <div className="alert alert-info" role="status">
            <strong>Hesabın henüz doğrulanmadı.</strong> Giriş yapabilirsin; mentor profili ve arama
            gibi işlemler hesabın doğrulandıktan sonra açılır.
          </div>
          <p className="text-muted">
            {createdUser.full_name}, {createdUser.email} adresiyle kaydoldun.
          </p>
          <Link to="/login" className="btn btn-primary">
            Giriş yap
          </Link>
        </section>
      </main>
    )
  }

  return (
    <main className="container container-narrow">
      <section className="card">
        <h1>Kayıt ol</h1>
        <p className="text-muted">
          Tek hesapla hem ders alabilir hem ders verebilirsin; kayıtta rol seçmen gerekmez.
        </p>

        {submitError && (
          <div className="alert alert-error" role="alert">
            {submitError}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <Field
            id="fullName"
            label="Ad soyad"
            autoComplete="name"
            maxLength={100}
            value={form.fullName}
            onChange={update('fullName')}
            error={errors.fullName}
          />
          <Field
            id="email"
            label="E-posta"
            type="email"
            autoComplete="email"
            maxLength={254}
            value={form.email}
            onChange={update('email')}
            error={errors.email}
          />
          <Field
            id="password"
            label="Parola"
            type="password"
            autoComplete="new-password"
            maxLength={128}
            value={form.password}
            onChange={update('password')}
            hint="En az 8 karakter."
            error={errors.password}
          />
          <Field
            id="passwordAgain"
            label="Parola (tekrar)"
            type="password"
            autoComplete="new-password"
            maxLength={128}
            value={form.passwordAgain}
            onChange={update('passwordAgain')}
            error={errors.passwordAgain}
          />
          <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
            {saving ? 'Kaydediliyor…' : 'Kayıt ol'}
          </button>
        </form>

        <p className="form-footer">
          Zaten hesabın var mı? <Link to="/login">Giriş yap</Link>
        </p>
      </section>
    </main>
  )
}
