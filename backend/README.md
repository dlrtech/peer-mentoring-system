
# Peer Mentoring System - Backend

Akran Mentörlük Sistemi ortak backend altyapısı.

## Kullanılan Teknolojiler

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pytest
- Argon2-cffi
- PyJWT

## Kurulum

PostgreSQL üzerinde `akran_mentorluk` isimli
bir veritabanı oluşturun.

Backend klasörüne geçin:

```bash
cd backend
```

### Windows (PowerShell)

Python sanal ortamını oluşturun:

```powershell
python -m venv .venv
```

Sanal ortamı etkinleştirin:

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

Python sanal ortamını oluşturun:

```bash
python3 -m venv .venv
```

Sanal ortamı etkinleştirin:

```bash
source .venv/bin/activate
```

### Bağımlılıkların Kurulumu

Gerekli kütüphaneleri yükleyin:

```bash
python -m pip install -r requirements.txt
```

Bağımlılık uyumluluğunu kontrol edin:

```bash
python -m pip check
```

## Ortam Değişkenleri

`.env.example` dosyasını `.env` olarak kopyalayın.

Mevcut bir `.env` dosyanız varsa üzerine yazmayın.

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

### Ortam Değişkenlerinin Yapılandırılması

- DATABASE_URL: Yerel PostgreSQL bağlantı adresi
- FRONTEND_URL: Frontend uygulamasının adresi
- SECRET_KEY: JWT imzalama için gizli anahtar
- ALGORITHM: JWT algoritması (HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES: Token geçerlilik süresi (30)

DATABASE_URL içerisindeki PostgreSQL bağlantı
bilgilerini kendi yerel ortamınıza göre düzenleyin.

Güvenli ve rastgele bir SECRET_KEY oluşturmak için:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Üretilen anahtarı yerel `.env` dosyanızdaki
SECRET_KEY alanına ekleyin.

Gerçek şifreleri ve gizli anahtarları GitHub'a
yüklemeyin.

## Veritabanı Kurulumu

Yeni ve boş veritabanlarında migration işlemini
çalıştırın:

```bash
python -m alembic upgrade head
```

Migration ve model uyumluluğunu kontrol edin:

```bash
python -m alembic check
```

Ders kataloğunu yükleyin:

```bash
python -m scripts.seed_courses
```

Seed işlemi tekrar çalıştırılabilir.
Mevcut ders kodları yeniden eklenmez.

## Migration Sürüm Geçişi

Başlangıç migration'ları tek bir dosyada
birleştirilmiştir.

Güncel başlangıç sürümü:

64c9b382985b

Önceki 7a49541f4f15 sürümünü yerel veritabanına
uygulamış geliştiricilerin sürüm geçişi yapması
gerekmektedir.

Yeni kodları almadan önce:

1. Yerel veritabanının yedeğini alın.
2. Mevcut migration sürümünü kontrol edin.
3. Veritabanı şemasının güncel ORM modelleriyle
   uyumlu olduğunu doğrulayın.

```bash
python -m alembic current
python -m alembic check
```

Yalnızca mevcut veritabanı 7a49541f4f15
sürümündeyse ve şema kontrolü başarılıysa,
eski migration dosyaları henüz mevcutken
aşağıdaki komutu çalıştırın:

```bash
python -m alembic stamp 64c9b382985b
```

Ardından güncel branch kodlarını alın ve
migration durumunu tekrar kontrol edin:

```bash
python -m alembic current
python -m alembic check
```

Stamp işlemi tabloları yeniden oluşturmaz.
Yalnızca Alembic sürüm kaydını günceller.

Farklı bir migration sürümü veya şema
uyumsuzluğu varsa bu işlemi uygulamadan önce
backend sorumlusuyla iletişime geçin.

Downgrade işlemleri veri kaybına neden
olabileceğinden yalnızca ayrı test
veritabanlarında gerçekleştirilmelidir.

## Uygulamayı Çalıştırma

```bash
python -m uvicorn app.main:app --reload
```

Swagger:
http://localhost:8000/docs

Health Check:
http://localhost:8000/health

## Testler

```bash
python -m pytest tests -v
```

Mevcut entegrasyon testleri DATABASE_URL
üzerinden bağlantı kurmaktadır.

Migration ve veri değiştiren testler için
ayrı bir test veritabanı kullanılmalıdır.

## Veritabanı Tabloları

- users
- mentor_profiles
- courses
- mentor_courses

## Ders Modeli

- id: Benzersiz kayıt kimliği
- code: Benzersiz ve zorunlu ders kodu
- name: Zorunlu ancak benzersiz olmayan ders adı
- description: İsteğe bağlı ders açıklaması

Farklı ders kodlarına sahip aynı isimli
dersler bulunabilir.

Ders ilişkileri course_id üzerinden kurulur.

Bir öğrenci aynı hesap üzerinden hem mentörlük
yapabilir hem de mentörlük alabilir.

## Güvenlik

- Parola güvenliği için Argon2id kullanılır.
- JWT güvenlik modülü için PyJWT kullanılır.
- Gizli anahtarlar ortam değişkenlerinde tutulur.
- Parolalar düz metin olarak saklanmamalıdır.
- .env ve .venv GitHub'a yüklenmemelidir.
- Her geliştirici kendi yerel PostgreSQL
  veritabanını kullanmalıdır.

Güvenlik modülünün ve kimlik doğrulama
endpoint'lerinin uygulama durumu ilgili
Pull Request'ler üzerinden takip edilir.

## Proje Dokümanları

- [Sistem Mimarisi](../docs/architecture.md)
- [API Sözleşmesi](../docs/api-contract.md)