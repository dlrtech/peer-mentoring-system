# Faz 3 Kararları

Bu dosya Faz 3 boyunca ekipçe alınan kararların kaydıdır. Yeni karar
alındığında ilgili bölüme eklenir; değişen karar silinmez, tarihiyle
birlikte güncellenir.

## 1. Repo ve branch adları

Repository: `dlrtech/peer-mentoring-system`

| Branch | Amaç |
|---|---|
| `main` | Test edilmiş, demo için hazır kod. Kimse doğrudan push yapmaz. |
| `develop` | Ortak entegrasyon branch'i. Tüm PR'lar buraya açılır. |
| `setup/frontend`, `setup/backend`, `setup/security` | Geçici altyapı branch'leri (Berat, Tuğba, Mert). |
| `feature/<ad>-<konu>` | Kişisel geliştirme branch'leri. |

Kişisel branch adları:

| Kişi | Branch |
|---|---|
| Dilara | `feature/dilara-auth` |
| Berat | `feature/berat-frontend` |
| Miraç | `feature/mirac-profile-search` |
| Hilal | `feature/hilal-tests` |

Kurallar:

- Her değişiklik Pull Request ile `develop`'a girer; PR'lar `main`'e değil
  `develop`'a açılır.
- Her PR en az bir kişi tarafından incelenir; inceleme bulguları aynı
  branch'e yeni commit olarak işlenir.
- Gerçek `.env` dosyaları repoya yüklenmez; yalnızca `.env.example` paylaşılır.

## 2. Ders modeli

- Faz 3 planında `courses.name` UNIQUE idi. Gerçek ders kataloğunda aynı
  isimli fakat farklı kodlu dersler bulunduğu için benzersizlik `code`
  alanına taşındı; `name` benzersiz değildir. (PR #5)
- Ders ilişkileri ve API istekleri `course_id` ile kurulur, ders adıyla değil.
- Ayrıntılar: `docs/architecture.md`, `docs/api-contract.md`.

## 3. Kayıt ve giriş (UC-1)

- Kalıcı rol seçimi yoktur. Aynı hesap hem mentor hem mentee olabilir.
- `POST /auth/register` → 201, yanıt: `id`, `full_name`, `email`, `is_verified`.
- `POST /auth/login` → 200, yanıt: `access_token`, `token_type`.
- E-posta küçük harfe çevrilerek saklanır ve karşılaştırılır.
- Alan sınırları: ad soyad 2–100, e-posta en fazla 254, parola 8–128 karakter.
  Frontend doğrulamasıyla aynıdır.
- Yeni hesap `is_verified=false` açılır. `is_verified` ve `is_admin`
  istemciden kabul edilmez (gönderilirse 422).
- Doğrulanmamış hesap giriş yapabilir; korumalı işlemlerde 403 alır.
- Yanlış parola ve kayıtsız e-posta aynı 401 mesajını döner; böylece hesabın
  var olup olmadığı anlaşılmaz.
- Gerçek e-posta doğrulaması Faz 4'e bırakıldı.

Hata kodları:

| Kod | Durum |
|---|---|
| 401 | Hatalı giriş veya eksik/geçersiz token |
| 403 | Doğrulanmamış veya yetkisiz kullanıcı |
| 404 | Olmayan profil veya ders |
| 409 | Mükerrer kayıt |
| 422 | Geçersiz veri |

## 4. Güvenlik ve ortam

- Parola hash'i: Argon2id. JWT: `sub` kullanıcı ID'si (metin), `exp` zorunlu.
- CORS yalnız `FRONTEND_URL` origin'ine izin verir. Token çerezle değil
  `Authorization` başlığıyla gittiği için `allow_credentials=False`.
- Token demo için frontend'de bellekte tutulur; sayfa yenilenince yeniden
  giriş gerekir.

## 5. Veritabanı ve seed

- Herkes kendi yerel PostgreSQL veritabanını kullanır; ortak olan model ve
  migration dosyalarıdır.
- Şema Alembic ile yönetilir; başlangıç migration'ı tek dosyadır.
- Ders kataloğu `python -m scripts.seed_courses` ile yüklenir (planda
  `python -m app.seed` yazıyordu). Komut tekrar çalıştırılabilir.

## 6. Açık konular

- `GET /auth/me`: frontend (`authApi.js`) çağırıyor, ekip sözleşmesinde yok.
  `get_current_user` develop'a geldikten sonra eklenecek.
- Entegrasyon testleri şu an geliştirme veritabanına bağlanıyor; Hilal'in
  ayrı test veritabanı planıyla birlikte ele alınacak.
- Mesaj saklama süresi ve KVKK politikası ayrıca kararlaştırılacak.
- Faz 4 ve Faz 5 kapsamı, resmi isterler paylaşılana kadar geçicidir.
