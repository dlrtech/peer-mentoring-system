// Arama sonucundaki tek bir mentoru gösteren kart (sorumlu: Miraç).
// Beklenen veri: { mentor_id, full_name, department, bio, courses: [{ id, code, name }] }
// Randevu talebi düğmesi Faz 4'te eklenecek.

import { courseLabel } from '../services/mentorApi.js'

const tagListStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 'var(--space-2)',
  listStyle: 'none',
  padding: 0,
  margin: 0,
}

const tagStyle = {
  background: 'var(--color-bg)',
  border: '1px solid var(--color-border)',
  borderRadius: '999px',
  padding: '2px var(--space-3)',
  fontSize: '0.875rem',
}

export default function MentorCard({ mentor }) {
  const { full_name: fullName, department, bio, courses = [] } = mentor

  return (
    <article className="card">
      <h3 style={{ marginBottom: 'var(--space-1)' }}>{fullName}</h3>
      <p className="text-muted" style={{ marginBottom: 'var(--space-3)' }}>
        {department}
      </p>
      <p>{bio}</p>
      {courses.length > 0 && (
        <>
          <span className="visually-hidden">Verdiği dersler:</span>
          <ul style={tagListStyle}>
            {courses.map((course) => (
              <li key={course.id} style={tagStyle}>
                {courseLabel(course)}
              </li>
            ))}
          </ul>
        </>
      )}
    </article>
  )
}
