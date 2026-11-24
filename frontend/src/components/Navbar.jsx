// Üst menü (sorumlu: Berat). Giriş durumuna göre linkler değişir.

import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import { isMockMode } from '../services/authApi.js'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <header className="navbar">
      <a href="#main" className="skip-link">
        İçeriğe geç
      </a>
      <nav className="navbar-inner" aria-label="Ana menü">
        <NavLink to="/" className="navbar-brand" end>
          Akran Mentörlük
        </NavLink>

        {isMockMode && (
          <span className="badge badge-warning" title="VITE_USE_MOCK=true">
            Örnek veri modu
          </span>
        )}

        <ul className="navbar-links">
          {isAuthenticated ? (
            <>
              <li>
                <NavLink to="/mentor/profile">Mentor profilim</NavLink>
              </li>
              <li>
                <NavLink to="/mentor/search">Mentor ara</NavLink>
              </li>
              <li className="navbar-user" aria-label="Giriş yapan kullanıcı">
                {user.full_name || user.email}
              </li>
              <li>
                <button
                  type="button"
                  className="btn btn-secondary btn-small"
                  onClick={handleLogout}
                >
                  Çıkış yap
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <NavLink to="/login">Giriş yap</NavLink>
              </li>
              <li>
                <NavLink to="/register">Kayıt ol</NavLink>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  )
}
