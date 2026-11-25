
# Akran Mentörlük Sistemi - Sistem Mimarisi

## 1. Genel Mimari

Akran Mentörlük Sistemi, üniversite öğrencilerinin ders bazlı
mentörlük almasını ve vermesini sağlayan web tabanlı bir uygulamadır.

Sistem üç temel katmandan oluşur:

- Frontend: React ve Vite
- Backend: Python 3.12 ve FastAPI
- Veritabanı: PostgreSQL

Backend tarafında SQLAlchemy ORM, Alembic migration yönetimi
ve Pytest test altyapısı kullanılmaktadır.

## 2. Kullanıcı Modeli

Bir öğrenci aynı kullanıcı hesabıyla hem mentörlük yapabilir
hem de mentörlük alabilir.

Mentör ve mentee için ayrı kullanıcı tabloları bulunmaz.
Mentörlük yapmak isteyen kullanıcı bir mentör profili oluşturur.

### users

| Alan | Veri tipi | Kısıt |
|---|---|---|
| id | Integer | Primary Key |
| full_name | String(150) | NOT NULL |
| email | String(255) | UNIQUE, NOT NULL |
| password_hash | String(255) | NOT NULL |
| is_verified | Boolean | NOT NULL, Default: false |
| is_admin | Boolean | NOT NULL, Default: false |
| created_at | DateTime | NOT NULL |

### mentor_profiles

| Alan | Veri tipi | Kısıt |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | Foreign Key, UNIQUE, NOT NULL |
| bio | Text | NOT NULL |
| department | String(150) | NOT NULL |
| created_at | DateTime | NOT NULL |

## 3. Ders Modeli

### courses

| Alan | Veri tipi | Kısıt |
|---|---|---|
| id | Integer | Primary Key |
| code | String(20) | UNIQUE, NOT NULL |
| name | String(150) | NOT NULL |
| description | Text | Nullable |

### Ders Benzersizliği Kararı

Derslerin benzersizliği ders adı yerine ders kodu üzerinden
sağlanmaktadır.

Üniversitenin gerçek ders kataloğunda aynı isimli fakat farklı
kodlara sahip dersler bulunabilmektedir.

Bu nedenle:

- code alanı benzersiz ve zorunludur.
- name alanı zorunludur ancak benzersiz değildir.
- description alanı isteğe bağlıdır.
- Ders ilişkileri id alanı üzerinden kurulur.
- Ders seçimlerinde yalnızca ders adı kullanılmamalıdır.
- Frontend ekranlarında ders kodu ve ders adı birlikte gösterilebilir.

Bu karar, Faz 3 planındaki courses.name UNIQUE yaklaşımının
gerçek ders kataloğuna uygun olarak güncellenmesidir.

### mentor_courses

| Alan | Veri tipi | Kısıt |
|---|---|---|
| id | Integer | Primary Key |
| mentor_id | Integer | Foreign Key, NOT NULL |
| course_id | Integer | Foreign Key, NOT NULL |

mentor_id ve course_id alanlarının birleşimi benzersizdir.

Böylece aynı mentör aynı dersi birden fazla kez ekleyemez.

## 4. Veritabanı İlişkileri

- users ve mentor_profiles: Bire sıfır veya bir (1 - 0..1)
- mentor_profiles ve mentor_courses: Bire çok (1 - N)
- courses ve mentor_courses: Bire çok (1 - N)

Mentör profilleri ve dersler arasında mentor_courses tablosu
aracılığıyla çoka çok ilişki kurulur.

## 5. Migration ve Seed Yönetimi

Veritabanı şeması Alembic ile yönetilmektedir.

Başlangıç migration sürümü: 64c9b382985b

Ders kodu başlangıç migration'ına dahil edilmiştir.

Ders kataloğu scripts.seed_courses modülü ile yüklenmektedir.
Seed işlemi tekrar çalıştırıldığında aynı ders koduna sahip
kayıtlar yeniden oluşturulmaz.

## 6. Güvenlik Mimarisi

Güvenlik modülünde kullanılan bileşenler:

- Argon2id ile parola hashleme
- JWT ile kimlik doğrulama
- Authorization Bearer başlığı ile token iletimi
- Ortam değişkenleri üzerinden gizli anahtar yönetimi
- Veritabanı üzerinden kullanıcı doğrulama ve yetki kontrolü

Gerçek parolalar ve gizli anahtarlar kaynak kodda tutulmamalıdır.

Her geliştirici kendi yerel PostgreSQL veritabanını ve
.env dosyasını kullanmalıdır.

## 7. API ve Frontend Uyumluluğu

Frontend ve backend arasındaki veri alışverişi JSON formatında
gerçekleştirilir.

API sözleşmeleri api-contract.md dosyasında tanımlanır.

Ders seçimi, mentör profili ve mentör arama işlemlerinde ortak
ders modeli kullanılmalıdır.

## 8. Kalite ve Test

Altyapı doğrulama süreçleri:

- Birim testleri
- Entegrasyon testleri
- Migration upgrade ve downgrade testleri
- Migration ve ORM model uyumluluğu
- Seed tekrar çalıştırılabilirlik kontrolü
- Bağımsız kod incelemesi

## 9. Mimari Alternatifler ve Mimari Karar

| Mimari | Avantajlar | Dezavantajlar |
|---|---|---|
| Basit monolit | Hızlı geliştirme, kolay kurulum | Modüller arasında yüksek bağımlılık riski |
| Modüler monolit | Modüler geliştirme, test edilebilirlik, kolay entegrasyon | Modül sınırlarının korunması gerekir |
| Mikroservis | Bağımsız dağıtım ve ölçeklendirme | Yüksek altyapı, iletişim ve entegrasyon maliyeti |

### Seçilen Mimari: Modüler Monolit

Akran Mentörlük Sistemi için modüler monolit mimarisi kullanılmaktadır.

Bu mimarinin tercih edilme nedenleri:

- Yedi kişilik geliştirme ekibine uygun olması.
- Kısa geliştirme süresinde entegrasyonu kolaylaştırması.
- Modüllerin birbirinden bağımsız geliştirilebilmesi.
- Birim ve entegrasyon testlerini kolaylaştırması.
- Mikroservis mimarisinin ek altyapı maliyetlerini gerektirmemesi.
- Sonraki fazlarda yeni modüllerin eklenmesine uygun olması.

### Katmanlı Backend Yapısı

- Routers: HTTP isteklerinin karşılanması.
- Schemas: Pydantic ile veri doğrulama ve yanıt modelleri.
- Services: İş mantığı ve veritabanı işlemleri.
- Models: SQLAlchemy veritabanı modelleri.
- Security: Kimlik doğrulama, parola güvenliği ve yetkilendirme.
- Database: Veritabanı bağlantısı ve oturum yönetimi.

Frontend, REST/JSON üzerinden FastAPI uygulamasıyla iletişim kurar. Backend, SQLAlchemy aracılığıyla PostgreSQL veritabanına erişir.

## 10. Demo Verisi Yönetimi

Ders kataloğu oluşturma komutu:

`python -m scripts.seed_courses`

Doğrulanmış demo kullanıcılarını oluşturma komutu:

`python -m scripts.seed_demo_users`

Demo kullanıcıları:

- dogrulanmis@ornek.edu.tr
- deniz@ornek.edu.tr

Demo parolaları yerel .env dosyasındaki DEMO_USER_PASSWORD değişkeninden okunur ve Argon2id ile hashlenir.

Her iki seed işlemi tekrar çalıştırılabilir ve mevcut kayıtların mükerrer oluşturulmasını engeller.

Yeni kayıt olan kullanıcılar varsayılan olarak doğrulanmamıştır. Gerçek e-posta doğrulaması Faz 4 kapsamında gerçekleştirilecektir.

## 11. Faz 3 Güvenlik ve Doğrulama Durumu

- Argon2id parola hashleme uygulanmıştır.
- JWT Bearer kimlik doğrulaması uygulanmıştır.
- Korumalı profil ve ders API'lerinde doğrulanmış kullanıcı kontrolü bulunmaktadır.
- Profil sahipliği token üzerinden belirlenmektedir.
- Mükerrer profil ve ders kayıtları engellenmektedir.
- Pydantic ile giriş verileri doğrulanmaktadır.
- SQLAlchemy ORM üzerinden parametreli veritabanı işlemleri gerçekleştirilmektedir.
- CORS, yapılandırılmış frontend adresiyle sınırlandırılmıştır.
- Gerçek ortam ayarları Git tarafından takip edilmemektedir.

## 12. Faz 3 Backend Doğrulama Sonuçları

24 Kasım 2026 tarihinde gerçekleştirilen kontroller:

- Pytest: 56 başarılı test, 1 deprecation uyarısı.
- Pip check: Bağımlılık hatası bulunmamıştır.
- Alembic current: 64c9b382985b (head).
- Alembic check: Yeni migration gereksinimi bulunmamıştır.
- Swagger: Profil oluşturma, profil görüntüleme, ders listeleme ve ders ekleme işlemleri başarılıdır.
- Negatif testler: 401, 403, 404, 409 ve 422 hata senaryoları kontrol edilmiştir.
- Demo kullanıcıları: Seed ve parola doğrulama işlemleri başarılıdır.

Bu sonuçlar PR #11 öncesindeki backend sürümüne aittir. Tüm ekip modülleri birleştirildikten sonra entegrasyon ve regresyon testleri yeniden gerçekleştirilecektir.