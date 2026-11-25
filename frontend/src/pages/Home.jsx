// Ana sayfa (sorumlu: Berat). Rota: /
// Giriş yapmamış kullanıcı: kısa tanıtım + Giriş / Kayıt.
// Giriş yapmış kullanıcı: aynı hesapta iki seçenek birlikte — Ders ver ve Ders al.

import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'

function VerificationNotice({ isVerified }) {
  if (isVerified === true) return null
  if (isVerified === false) {
    return (
      <div className="alert alert-warning" role="status">
        <strong>Hesabın henüz doğrulanmadı.</strong> Mentor profili oluşturma ve mentor arama
        hesabın doğrulandıktan sonra açılır.
      </div>
    )
  }
  return null // Doğrulama durumu bilinmiyor (/auth/me henüz yok)
}

export default function Home() {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return (
      <main className="container">
        <section className="hero">
          <h1>Akran Mentörlük</h1>
          <p className="text-muted">
            Zorlandığın derste üst sınıflardan destek al, iyi olduğun derste başkalarına yardım et.
            Tek hesapla ikisini de yapabilirsin.
          </p>
          <div className="actions">
            <Link to="/register" className="btn btn-primary">
              Kayıt ol
            </Link>
            <Link to="/login" className="btn btn-secondary">
              Giriş yap
            </Link>
          </div>
        </section>
      </main>
    )
  }

  const greetingName = user.full_name || user.email

  return (
    <main className="container">
      <h1>Merhaba, {greetingName}</h1>
      <VerificationNotice isVerified={user.is_verified} />
      <p className="text-muted">Bugün ne yapmak istersin?</p>

      <div className="choice-grid">
        <section className="card choice-card" aria-labelledby="choice-teach">
          <h2 id="choice-teach">Ders ver</h2>
          <p className="text-muted">
            Mentor profilini oluştur, verebileceğin dersleri ekle; diğer öğrenciler seni aramada
            bulsun.
          </p>
          <Link to="/mentor/profile" className="btn btn-primary">
            Mentor profilime git
          </Link>
        </section>

        <section className="card choice-card" aria-labelledby="choice-learn">
          <h2 id="choice-learn">Ders al</h2>
          <p className="text-muted">Zorlandığın dersin adını yaz, o dersi veren akranlarını bul.</p>
          <Link to="/mentor/search" className="btn btn-primary">
            Mentor ara
          </Link>
        </section>
      </div>
    </main>
  )
}
