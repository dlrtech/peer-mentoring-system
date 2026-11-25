// Mentor profili, ders listesi ve mentor arama istekleri (sorumlu: Miraç).
// Tüm istekler Berat'ın ortak api.js katmanından geçer; token ve hata mesajları orada yönetilir.
//
// Örnek veri modu: backend hazır olmadan ekranları denemek için
// frontend/.env içine VITE_USE_MOCK=true yazılır. Gerçek API için satır silinir veya false yapılır.
// Örnek veriler docs/api-contract.md'deki JSON örnekleriyle aynı alan adlarını kullanır.

import { api, ApiError } from './api.js'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// --- Gerçek API ---

const realApi = {
  getMyProfile: () => api.get('/mentors/profile'),
  createProfile: ({ bio, department }) => api.post('/mentors/profile', { bio, department }),
  getCourses: () => api.get('/courses'),
  addCourse: (courseId) => api.post('/mentors/courses', { course_id: courseId }),
  searchMentors: (courseName, options) =>
    api.get(`/mentors/search?course_name=${encodeURIComponent(courseName)}`, options),
}

// --- Örnek veri (yalnızca VITE_USE_MOCK=true iken) ---

const MOCK_USER_ID = 1

const mockCourses = [
  { id: 1, code: 'BYM105', name: 'Matematik I', description: null },
  { id: 2, code: 'BYM224', name: 'Veri Yapıları ve Algoritmalar', description: null },
  { id: 3, code: 'BYM302', name: 'Algoritma Analizi', description: null },
  { id: 4, code: 'BYM301', name: 'Veritabanı Yönetimi', description: null },
  { id: 5, code: 'BYM216', name: 'Nesne Yönelimli Programlama', description: null },
  // Sözleşme gereği ders adı benzersiz değildir; aynı isimli iki ders kodlarıyla ayrılır.
  { id: 6, code: 'BYM222', name: 'Görüntü İşleme', description: null },
  { id: 7, code: 'BYM452', name: 'Görüntü İşleme', description: null },
]

// Başka öğrencilerin profilleri (aramada görünür).
const mockOtherMentors = [
  {
    mentor_id: 2,
    full_name: 'Zeynep Arslan',
    department: 'Yazılım Mühendisliği',
    bio: 'Matematik ve algoritma dersi verebilirim.',
    courses: [
      { id: 1, code: 'BYM105', name: 'Matematik I' },
      { id: 3, code: 'BYM302', name: 'Algoritma Analizi' },
    ],
  },
  {
    mentor_id: 3,
    full_name: 'Can Demir',
    department: 'Bilgisayar Mühendisliği',
    bio: 'Veri yapıları ve OOP konularında yardımcı olurum.',
    courses: [
      { id: 2, code: 'BYM224', name: 'Veri Yapıları ve Algoritmalar' },
      { id: 5, code: 'BYM216', name: 'Nesne Yönelimli Programlama' },
      { id: 6, code: 'BYM222', name: 'Görüntü İşleme' },
    ],
  },
]

// Giriş yapan öğrencinin profili; başlangıçta yok (404 ekranını denemek için).
let mockMyProfile = null
let mockNextId = 10

const delay = (ms = 300) => new Promise((resolve) => setTimeout(resolve, ms))
const copy = (value) => structuredClone(value)

const mockApi = {
  async getMyProfile() {
    await delay()
    if (!mockMyProfile) throw new ApiError(404, 'Mentor profili bulunamadı', { hadToken: true })
    return copy(mockMyProfile)
  },
  async createProfile({ bio, department }) {
    await delay()
    if (mockMyProfile) throw new ApiError(409, 'Profil zaten var', { hadToken: true })
    mockMyProfile = {
      id: 1,
      user_id: MOCK_USER_ID,
      bio: bio.trim(),
      department: department.trim(),
      courses: [],
    }
    return copy(mockMyProfile)
  },
  async getCourses() {
    await delay()
    return copy(mockCourses)
  },
  async addCourse(courseId) {
    await delay()
    if (!mockMyProfile) throw new ApiError(404, 'Mentor profili bulunamadı', { hadToken: true })
    const course = mockCourses.find((item) => item.id === courseId)
    if (!course) throw new ApiError(404, 'Ders bulunamadı', { hadToken: true })
    if (mockMyProfile.courses.some((item) => item.id === courseId)) {
      throw new ApiError(409, 'Ders zaten ekli', { hadToken: true })
    }
    mockMyProfile.courses.push({ id: course.id, code: course.code, name: course.name })
    return { id: mockNextId++, mentor_id: mockMyProfile.id, course_id: courseId }
  },
  async searchMentors(courseName) {
    await delay()
    const query = courseName.trim().toLocaleLowerCase('tr')
    // Kendi profili sözleşme gereği aramada çıkmaz; bu yüzden mockMyProfile eklenmez.
    return copy(
      mockOtherMentors.filter((mentor) =>
        mentor.courses.some((course) => course.name.toLocaleLowerCase('tr').includes(query)),
      ),
    )
  },
}

const source = USE_MOCK ? mockApi : realApi

// Ders adları benzersiz olmadığı için (api-contract.md) ekranda kod + ad birlikte gösterilir.
// Örn. "BYM222 · Görüntü İşleme". Kod yoksa yalnızca ad.
export function courseLabel(course) {
  if (!course) return 'Ders'
  return course.code ? `${course.code} · ${course.name}` : course.name
}

export const isMockMode = USE_MOCK

// GET /mentors/profile — giriş yapan öğrencinin profili. Profil yoksa ApiError(404).
export const getMyProfile = () => source.getMyProfile()

// POST /mentors/profile — { bio, department }
export const createProfile = (data) => source.createProfile(data)

// GET /courses — ortak ders listesi
export const getCourses = () => source.getCourses()

// POST /mentors/courses — { course_id }
export const addCourse = (courseId) => source.addCourse(courseId)

// GET /mentors/search?course_name=... — sonuç yoksa []
export const searchMentors = (courseName, options) => source.searchMentors(courseName, options)
