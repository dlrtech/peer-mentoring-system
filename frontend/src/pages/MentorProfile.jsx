// Mentor profili ekranı (sorumlu: Miraç). Rota: /mentor/profile
// - Profil yoksa (GET 404) profil oluşturma formu gösterilir.
// - Profil varsa bilgiler, verilen dersler ve ders ekleme bölümü gösterilir.
// Aynı hesap ders vermeye devam ederken /mentor/search ile başka mentor da arayabilir.

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { addCourse, createProfile, getCourses, getMyProfile } from '../services/mentorApi.js'

const BIO_MAX = 500
const DEPARTMENT_MIN = 2
const DEPARTMENT_MAX = 100

function validateProfile({ bio, department }) {
  const errors = {}
  const cleanBio = bio.trim()
  const cleanDepartment = department.trim()
  if (!cleanBio) errors.bio = 'Kısa bir tanıtım yaz.'
  else if (cleanBio.length > BIO_MAX) errors.bio = `Tanıtım en fazla ${BIO_MAX} karakter olabilir.`
  if (cleanDepartment.length < DEPARTMENT_MIN)
    errors.department = 'Bölüm adı en az 2 karakter olmalı.'
  else if (cleanDepartment.length > DEPARTMENT_MAX)
    errors.department = `Bölüm adı en fazla ${DEPARTMENT_MAX} karakter olabilir.`
  return errors
}

function CreateProfileForm({ onCreated }) {
  const [form, setForm] = useState({ bio: '', department: '' })
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [saving, setSaving] = useState(false)

  function update(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const found = validateProfile(form)
    setErrors(found)
    if (Object.keys(found).length > 0) return

    setSaving(true)
    setSubmitError('')
    try {
      const profile = await createProfile({
        bio: form.bio.trim(),
        department: form.department.trim(),
      })
      onCreated(profile)
    } catch (error) {
      if (error.status === 409) {
        setSubmitError('Zaten bir mentor profilin var. Sayfayı yenileyip tekrar dene.')
      } else {
        setErrors(error.fieldErrors ?? {})
        setSubmitError(error.message)
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="card">
      <h2>Mentor profili oluştur</h2>
      <p className="text-muted">
        Henüz mentor profilin yok. Profil oluşturunca ders ekleyebilir ve diğer öğrencilerin
        aramalarında görünebilirsin. Ders almaya devam etmek için ayrı hesap gerekmez.
      </p>

      {submitError && (
        <div className="alert alert-error" role="alert">
          {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="department">Bölüm</label>
          <input
            id="department"
            value={form.department}
            onChange={update('department')}
            placeholder="Örn. Yazılım Mühendisliği"
            maxLength={DEPARTMENT_MAX}
            aria-invalid={errors.department ? 'true' : 'false'}
            aria-describedby={errors.department ? 'department-error' : undefined}
          />
          {errors.department && (
            <span id="department-error" className="field-error">
              {errors.department}
            </span>
          )}
        </div>

        <div className="field">
          <label htmlFor="bio">Kendini tanıt</label>
          <textarea
            id="bio"
            rows={4}
            value={form.bio}
            onChange={update('bio')}
            placeholder="Örn. Matematik ve algoritma dersi verebilirim."
            maxLength={BIO_MAX}
            aria-invalid={errors.bio ? 'true' : 'false'}
            aria-describedby={errors.bio ? 'bio-error bio-count' : 'bio-count'}
          />
          <span id="bio-count" className="text-muted" style={{ fontSize: '0.875rem' }}>
            {form.bio.trim().length}/{BIO_MAX}
          </span>
          {errors.bio && (
            <span id="bio-error" className="field-error">
              {errors.bio}
            </span>
          )}
        </div>

        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Kaydediliyor…' : 'Profili oluştur'}
        </button>
      </form>
    </section>
  )
}

function CourseSection({ profile, onCourseAdded }) {
  const [courses, setCourses] = useState([])
  const [coursesError, setCoursesError] = useState('')
  const [selectedId, setSelectedId] = useState('')
  const [adding, setAdding] = useState(false)
  const [message, setMessage] = useState(null) // { type: 'success' | 'error', text }

  useEffect(() => {
    let active = true
    getCourses()
      .then((data) => active && setCourses(Array.isArray(data) ? data : []))
      .catch((error) => active && setCoursesError(error.message))
    return () => {
      active = false
    }
  }, [])

  const myCourseIds = new Set(profile.courses.map((course) => course.id))
  const availableCourses = courses.filter((course) => !myCourseIds.has(course.id))

  async function handleAdd(event) {
    event.preventDefault()
    if (!selectedId) {
      setMessage({ type: 'error', text: 'Eklemek için bir ders seç.' })
      return
    }
    const courseId = Number(selectedId)
    setAdding(true)
    setMessage(null)
    try {
      await addCourse(courseId)
      const course = courses.find((item) => item.id === courseId)
      onCourseAdded({ id: courseId, name: course?.name ?? 'Ders' })
      setSelectedId('')
      setMessage({ type: 'success', text: `${course?.name ?? 'Ders'} profiline eklendi.` })
    } catch (error) {
      const text =
        error.status === 409
          ? 'Bu ders zaten profilinde ekli.'
          : error.status === 404
            ? 'Seçilen ders bulunamadı. Listeyi yenileyip tekrar dene.'
            : error.message
      setMessage({ type: 'error', text })
    } finally {
      setAdding(false)
    }
  }

  return (
    <section className="card" style={{ marginTop: 'var(--space-6)' }}>
      <h2>Verdiğin dersler</h2>

      {profile.courses.length === 0 ? (
        <p className="text-muted">Henüz ders eklemedin. Aşağıdan ilk dersini ekle.</p>
      ) : (
        <ul>
          {profile.courses.map((course) => (
            <li key={course.id}>{course.name}</li>
          ))}
        </ul>
      )}

      {message && (
        <div
          className={`alert alert-${message.type}`}
          role={message.type === 'error' ? 'alert' : 'status'}
        >
          {message.text}
        </div>
      )}

      {coursesError ? (
        <div className="alert alert-error" role="alert">
          Ders listesi yüklenemedi: {coursesError}
        </div>
      ) : (
        <form onSubmit={handleAdd} noValidate>
          <div className="field">
            <label htmlFor="course-select">Ders ekle</label>
            <select
              id="course-select"
              value={selectedId}
              onChange={(event) => setSelectedId(event.target.value)}
              disabled={availableCourses.length === 0}
            >
              <option value="">
                {availableCourses.length === 0 && courses.length > 0
                  ? 'Tüm dersler ekli'
                  : 'Ders seç'}
              </option>
              {availableCourses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={adding || availableCourses.length === 0}
          >
            {adding ? 'Ekleniyor…' : 'Dersi ekle'}
          </button>
        </form>
      )}
    </section>
  )
}

export default function MentorProfile() {
  const [status, setStatus] = useState('loading') // loading | missing | ready | error
  const [profile, setProfile] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    let active = true
    getMyProfile()
      .then((data) => {
        if (!active) return
        setProfile({ ...data, courses: data.courses ?? [] })
        setStatus('ready')
      })
      .catch((error) => {
        if (!active) return
        if (error.status === 404) {
          setStatus('missing')
        } else {
          setErrorMessage(error.message)
          setStatus('error')
        }
      })
    return () => {
      active = false
    }
  }, [])

  function handleCreated(newProfile) {
    setProfile({ ...newProfile, courses: newProfile.courses ?? [] })
    setStatus('ready')
  }

  function handleCourseAdded(course) {
    setProfile((prev) => ({ ...prev, courses: [...prev.courses, course] }))
  }

  return (
    <main className="container">
      <h1>Mentor profilim</h1>

      {status === 'loading' && <p className="text-muted">Profil yükleniyor…</p>}

      {status === 'error' && (
        <div className="alert alert-error" role="alert">
          {errorMessage}
        </div>
      )}

      {status === 'missing' && <CreateProfileForm onCreated={handleCreated} />}

      {status === 'ready' && profile && (
        <>
          <section className="card">
            <p className="text-muted" style={{ marginBottom: 'var(--space-1)' }}>
              Bölüm
            </p>
            <p>{profile.department}</p>
            <p className="text-muted" style={{ marginBottom: 'var(--space-1)' }}>
              Tanıtım
            </p>
            <p style={{ marginBottom: 0 }}>{profile.bio}</p>
          </section>
          <CourseSection profile={profile} onCourseAdded={handleCourseAdded} />
        </>
      )}

      <p style={{ marginTop: 'var(--space-6)' }}>
        Sen de destek almak mı istiyorsun? <Link to="/mentor/search">Başka mentorları ara</Link>
      </p>
    </main>
  )
}
