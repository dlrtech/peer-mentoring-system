import { Link, Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import { useAuth } from './auth/AuthContext.jsx'
import Navbar from './components/Navbar.jsx'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'

// Sayfa rotaları bu dosyada toplanır (sorumlu: Berat).
// Kural: bir sayfa yalnızca ilgili modülü develop'a merge edildikten sonra buraya import edilir.
// Bekleyen: /mentor/profile ve /mentor/search (Miraç, PR #3) → RequireAuth içine eklenecek.

// Giriş yapmamış kullanıcıyı /login'e gönderir; girişten sonra geldiği sayfaya döner.
function RequireAuth() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return <Outlet />
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
    <>
      <Navbar />
      <div id="main" tabIndex={-1}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route element={<RequireAuth />}>
            {/* Miraç'ın sayfaları PR #3 merge edilince buraya eklenecek */}
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </>
  )
}
