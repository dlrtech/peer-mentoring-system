
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

Güvenlik modülünde kullanılması planlanan bileşenler:

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