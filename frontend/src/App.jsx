import { Link, Route, Routes } from 'react-router-dom'

// Sayfa rotaları bu dosyada toplanır (sorumlu: Berat).
// Kural: bir sayfa yalnızca ilgili modülü develop'a merge edildikten sonra buraya import edilir.
// Planlanan rotalar: /, /register, /login, /mentor/profile, /mentor/search

function SetupHome() {
  return (
    <main className="container">
      <h1>Akran Mentörlük</h1>
      <p className="text-muted">
        Frontend altyapısı hazır. Kayıt, giriş ve mentor ekranları modüller tamamlandıkça eklenecek.
      </p>
    </main>
  )
}

function NotFound() {
  return (
    <main className="container">
      <h1>Sayfa bulunamadı</h1>
      <p className="text-muted">Aradığın sayfa yok veya taşınmış olabilir.</p>
      <Link to="/">Ana sayfaya dön</Link>
    </main>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<SetupHome />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
