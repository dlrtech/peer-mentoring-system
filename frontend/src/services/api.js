// Ortak API katmanı: tüm frontend modülleri backend'e bu dosya üzerinden istek atar.
// - Adres .env içindeki VITE_API_URL'den okunur.
// - İstek ve yanıt gövdeleri JSON'dur.
// - Token ekip kararı gereği yalnızca bellekte tutulur (localStorage kullanılmaz);
//   sayfa yenilenince kullanıcı tekrar giriş yapar.

const API_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '')

let accessToken = null
let unauthorizedHandler = null

export function setToken(token) {
  accessToken = token || null
}

export function getToken() {
  return accessToken
}

export function clearToken() {
  accessToken = null
}

// Oturumlu bir istek 401 aldığında çağrılacak fonksiyon (ör. çıkış yapıp /login'e yönlendirme).
export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = typeof handler === 'function' ? handler : null
}

const DEFAULT_MESSAGES = {
  0: 'Sunucuya ulaşılamadı. Bağlantını kontrol edip tekrar dene.',
  400: 'İstek işlenemedi. Bilgileri kontrol edip tekrar dene.',
  401: 'Oturumun geçersiz veya süresi dolmuş. Lütfen tekrar giriş yap.',
  403: 'Bu işlem için yetkin yok.',
  404: 'Aradığın kayıt bulunamadı.',
  409: 'Bu kayıt zaten var.',
  422: 'Bazı alanlar geçersiz. Lütfen kontrol et.',
  500: 'Sunucuda bir hata oluştu. Lütfen daha sonra tekrar dene.',
}

function defaultMessage(status) {
  if (DEFAULT_MESSAGES[status]) return DEFAULT_MESSAGES[status]
  return status >= 500 ? DEFAULT_MESSAGES[500] : DEFAULT_MESSAGES[400]
}

// FastAPI 422 yanıtında detail bir listedir: [{ loc: ['body', 'email'], msg: '...' }].
// Bunu { email: '...' } biçimine çevirir; sayfalar alan altında hata göstermek için kullanır.
function toFieldErrors(detail) {
  if (!Array.isArray(detail)) return {}
  const errors = {}
  for (const item of detail) {
    const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null
    if (typeof field === 'string' && !errors[field]) errors[field] = item.msg ?? 'Geçersiz değer'
  }
  return errors
}

// Backend hatası. Kullanıcıya gösterilecek Türkçe mesaj `message` içindedir;
// backend'in ham cevabı (`detail`) sadece sayfaya özel karar vermek için tutulur, ekrana basılmaz.
export class ApiError extends Error {
  constructor(status, detail) {
    super(defaultMessage(status))
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
    this.fieldErrors = toFieldErrors(detail)
  }
}

async function readJson(response) {
  if (response.status === 204) return null
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

export async function apiRequest(path, { method = 'GET', body, headers = {}, signal } = {}) {
  const finalHeaders = { Accept: 'application/json', ...headers }
  if (body !== undefined) finalHeaders['Content-Type'] = 'application/json'
  const hadToken = Boolean(accessToken)
  if (hadToken) finalHeaders.Authorization = `Bearer ${accessToken}`

  let response
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers: finalHeaders,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    })
  } catch (error) {
    if (error?.name === 'AbortError') throw error
    throw new ApiError(0, null)
  }

  const data = await readJson(response)

  if (!response.ok) {
    if (response.status === 401 && hadToken && unauthorizedHandler) unauthorizedHandler()
    throw new ApiError(response.status, data?.detail ?? null)
  }

  return data
}

export const api = {
  get: (path, options) => apiRequest(path, { ...options, method: 'GET' }),
  post: (path, body, options) => apiRequest(path, { ...options, method: 'POST', body }),
  put: (path, body, options) => apiRequest(path, { ...options, method: 'PUT', body }),
  patch: (path, body, options) => apiRequest(path, { ...options, method: 'PATCH', body }),
  delete: (path, options) => apiRequest(path, { ...options, method: 'DELETE' }),
}
