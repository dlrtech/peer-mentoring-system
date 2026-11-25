// Kayıt, giriş ve oturumdaki kullanıcı istekleri (sorumlu: Berat).
// Tüm istekler ortak api.js katmanından geçer; token bellekte tutulur.
//
// Örnek veri modu: frontend/.env içine VITE_USE_MOCK=true yazılırsa backend olmadan çalışır.
// Örnek hesaplar (yalnızca örnek veri modunda, gerçek parola değildir):
//   dogrulanmis@ornek.edu.tr / OrnekParola123  → doğrulanmış hesap
//   yeni@ornek.edu.tr        / OrnekParola123  → doğrulanmamış hesap

import { api, ApiError, clearToken, setToken } from './api.js'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// --- Gerçek API ---

const realApi = {
  // POST /auth/register → 201 { id, full_name, email, is_verified }
  register: ({ fullName, email, password }) =>
    api.post('/auth/register', { full_name: fullName, email, password }),

  // POST /auth/login → 200 { access_token, token_type }
  login: ({ email, password }) => api.post('/auth/login', { email, password }),

  // GET /auth/me → 200 { id, full_name, email, is_verified }
  // Not: Bu uç ekip sözleşmesinde henüz yok; Dilara'dan istendi.
  getMe: () => api.get('/auth/me'),
}

// --- Örnek veri (yalnızca VITE_USE_MOCK=true iken) ---

const mockUsers = [
  {
    id: 1,
    full_name: 'Ayşe Yılmaz',
    email: 'dogrulanmis@ornek.edu.tr',
    password: 'OrnekParola123',
    is_verified: true,
  },
  {
    id: 2,
    full_name: 'Mehmet Kaya',
    email: 'yeni@ornek.edu.tr',
    password: 'OrnekParola123',
    is_verified: false,
  },
]
let mockCurrentUserId = null
const delay = (ms = 300) => new Promise((resolve) => setTimeout(resolve, ms))
const publicUser = ({ id, full_name, email, is_verified }) => ({
  id,
  full_name,
  email,
  is_verified,
})

const mockApi = {
  async register({ fullName, email, password }) {
    await delay()
    const normalized = email.trim().toLowerCase()
    if (mockUsers.some((user) => user.email === normalized)) {
      throw new ApiError(409, 'Email already registered')
    }
    const user = {
      id: mockUsers.length + 1,
      full_name: fullName.trim(),
      email: normalized,
      password,
      is_verified: false,
    }
    mockUsers.push(user)
    return publicUser(user)
  },
  async login({ email, password }) {
    await delay()
    const user = mockUsers.find((item) => item.email === email.trim().toLowerCase())
    if (!user || user.password !== password) throw new ApiError(401, 'Invalid credentials')
    mockCurrentUserId = user.id
    return { access_token: `mock-token-${user.id}`, token_type: 'bearer' }
  },
  async getMe() {
    await delay(100)
    const user = mockUsers.find((item) => item.id === mockCurrentUserId)
    if (!user) throw new ApiError(401, 'Not authenticated', { hadToken: true })
    return publicUser(user)
  },
}

const source = USE_MOCK ? mockApi : realApi

export const isMockMode = USE_MOCK

export function register(data) {
  return source.register(data)
}

// Giriş başarılıysa token'ı belleğe yazar ve kullanıcı bilgisini döndürür.
export async function login({ email, password }) {
  const { access_token: token } = await source.login({ email: email.trim(), password })
  setToken(token)
  try {
    return await source.getMe()
  } catch (error) {
    // /auth/me henüz yoksa (404/405) girişi bozmayalım; bildiğimiz kadarını döndürelim.
    if (error instanceof ApiError && (error.status === 404 || error.status === 405)) {
      return { email: email.trim().toLowerCase(), full_name: null, is_verified: null }
    }
    clearToken()
    throw error
  }
}

export function logout() {
  clearToken()
  if (USE_MOCK) mockCurrentUserId = null
}
