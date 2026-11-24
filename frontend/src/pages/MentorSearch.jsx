// Ders adına göre mentor arama ekranı (sorumlu: Miraç). Rota: /mentor/search
// Durumlar: başlangıç, yükleniyor, sonuç listesi, boş sonuç ([]), hata.
// Kendi profilini dışarıda bırakma işi backend'dedir (Yusuf, search.py).

import { useEffect, useRef, useState } from 'react'
import MentorCard from '../components/MentorCard.jsx'
import { searchMentors } from '../services/mentorApi.js'

const MAX_LENGTH = 100

const formStyle = {
  display: 'flex',
  gap: 'var(--space-2)',
  alignItems: 'flex-start',
  flexWrap: 'wrap',
}

const listStyle = {
  display: 'grid',
  gap: 'var(--space-4)',
  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
}

export default function MentorSearch() {
  const [courseName, setCourseName] = useState('')
  const [inputError, setInputError] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const [results, setResults] = useState([])
  const [errorMessage, setErrorMessage] = useState('')
  const [searchedFor, setSearchedFor] = useState('')
  const controllerRef = useRef(null)

  // Sayfadan çıkılırsa yarım kalan isteği iptal et.
  useEffect(() => () => controllerRef.current?.abort(), [])

  async function handleSubmit(event) {
    event.preventDefault()
    const query = courseName.trim()

    if (!query) {
      setInputError('Aramak için bir ders adı yaz.')
      return
    }
    if (query.length > MAX_LENGTH) {
      setInputError(`Ders adı en fazla ${MAX_LENGTH} karakter olabilir.`)
      return
    }
    setInputError('')

    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller

    setStatus('loading')
    setErrorMessage('')
    try {
      const data = await searchMentors(query, { signal: controller.signal })
      setResults(Array.isArray(data) ? data : [])
      setSearchedFor(query)
      setStatus('done')
    } catch (error) {
      if (error?.name === 'AbortError') return
      setErrorMessage(error?.fieldErrors?.course_name ?? error?.message ?? 'Arama yapılamadı.')
      setStatus('error')
    }
  }

  return (
    <main className="container">
      <h1>Mentor ara</h1>
      <p className="text-muted">
        Destek almak istediğin dersi yaz; o dersi veren öğrencileri listeleyelim.
      </p>

      <form
        onSubmit={handleSubmit}
        noValidate
        className="card"
        style={{ marginBottom: 'var(--space-6)' }}
      >
        <div className="field" style={{ marginBottom: 0 }}>
          <label htmlFor="course-name">Ders adı</label>
          <div style={formStyle}>
            <input
              id="course-name"
              type="search"
              value={courseName}
              onChange={(event) => setCourseName(event.target.value)}
              placeholder="Örn. Matematik"
              maxLength={MAX_LENGTH}
              aria-invalid={inputError ? 'true' : 'false'}
              aria-describedby={inputError ? 'course-name-error' : undefined}
              style={{ flex: '1 1 240px' }}
            />
            <button type="submit" className="btn btn-primary" disabled={status === 'loading'}>
              {status === 'loading' ? 'Aranıyor…' : 'Ara'}
            </button>
          </div>
          {inputError && (
            <span id="course-name-error" className="field-error">
              {inputError}
            </span>
          )}
        </div>
      </form>

      <section aria-live="polite">
        {status === 'error' && (
          <div className="alert alert-error" role="alert">
            {errorMessage}
          </div>
        )}

        {status === 'done' && results.length === 0 && (
          <div className="card">
            <h2 style={{ fontSize: '1.125rem' }}>Sonuç bulunamadı</h2>
            <p className="text-muted" style={{ marginBottom: 0 }}>
              “{searchedFor}” dersini veren başka bir mentor yok. Farklı bir ders adı veya daha kısa
              bir kelime dene.
            </p>
          </div>
        )}

        {status === 'done' && results.length > 0 && (
          <>
            <p className="text-muted">
              “{searchedFor}” için {results.length} mentor bulundu.
            </p>
            <div style={listStyle}>
              {results.map((mentor) => (
                <MentorCard key={mentor.mentor_id} mentor={mentor} />
              ))}
            </div>
          </>
        )}
      </section>
    </main>
  )
}
