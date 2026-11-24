# Akran Mentörlük — Frontend

React + Vite (JavaScript), React Router ve sade CSS.

## Kurulum

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Uygulama: http://localhost:5173 — API adresi `.env` içindeki `VITE_API_URL` (varsayılan http://localhost:8000).

## Komutlar

| Komut                             | Ne yapar                             |
| --------------------------------- | ------------------------------------ |
| `npm run dev`                     | Geliştirme sunucusunu açar           |
| `npm run build`                   | Üretim derlemesi (`dist/`)           |
| `npm run lint`                    | oxlint ile kod kontrolü              |
| `npm run format` / `format:check` | Prettier ile biçimlendirme / kontrol |

## Klasör yapısı ve kurallar

```
src/
  main.jsx          # React + Router başlangıcı
  App.jsx           # Sayfa rotaları (sorumlu: Berat)
  index.css         # Ortak stiller ve renk değişkenleri
  services/api.js   # Ortak API katmanı — tüm istekler buradan
  pages/            # Sayfalar (Register, Login, Home, MentorProfile, MentorSearch)
  components/       # Ortak bileşenler (Navbar, MentorCard)
```

- **İstekler:** Modül servisleri (`authApi.js`, `mentorApi.js`) `api.get/post(...)` kullanır; `fetch`'i doğrudan çağırmaz.
- **Token:** Yalnızca bellekte tutulur (`setToken` / `clearToken`). `localStorage` kullanılmaz.
- **Hatalar:** `ApiError` kullanıcıya gösterilecek Türkçe mesajı (`message`), HTTP kodunu (`status`) ve 422'de alan hatalarını (`fieldErrors`) taşır. Backend'in ham `detail` metni ekrana basılmaz.
- **Rotalar:** Yeni sayfa, modülü develop'a merge edildikten sonra `App.jsx`'e eklenir.
- **Güvenlik:** Kullanıcı metni her zaman düz metin olarak gösterilir; `dangerouslySetInnerHTML` kullanılmaz.
