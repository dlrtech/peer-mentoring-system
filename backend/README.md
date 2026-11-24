# Peer Mentoring System - Backend

Akran Mentörlük Sistemi ortak backend altyapısı.

## Kullanılan Teknolojiler

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pytest

## Kurulum

PostgreSQL üzerinde akran_mentorluk isimli
bir veritabanı oluşturun.

Backend klasörüne geçin:

```powershell
cd backend
```

Python sanal ortamını oluşturun:

```powershell
python -m venv .venv
```

Sanal ortamı etkinleştirin:

```powershell
.\.venv\Scripts\Activate.ps1
```

Gerekli kütüphaneleri yükleyin:

```powershell
python -m pip install -r requirements.txt
```

## Ortam Değişkenleri

.env.example dosyasını .env olarak kopyalayın:

```powershell
Copy-Item .env.example .env
```

DATABASE_URL içerisindeki PostgreSQL şifresini
kendi şifrenizle değiştirin.

Gerçek şifreleri ve gizli anahtarları GitHub'a
yüklemeyin.

## Veritabanı Kurulumu

```powershell
python -m alembic upgrade head
```

Ders kataloğunu yükleyin:

```powershell
python -m scripts.seed_courses
```

## Uygulamayı Çalıştırma

```powershell
python -m uvicorn app.main:app --reload
```

Swagger:
http://localhost:8000/docs

Health Check:
http://localhost:8000/health

## Testler

```powershell
python -m pytest tests -v
```

## Veritabanı Tabloları

- users
- mentor_profiles
- courses
- mentor_courses

## Ders Modeli

- id: Benzersiz kayıt kimliği
- code: Benzersiz ders kodu
- name: Ders adı
- description: İsteğe bağlı ders açıklaması

Bir öğrenci aynı hesap üzerinden hem mentörlük
yapabilir hem de mentörlük alabilir.

## Güvenlik

.env ve .venv dosyaları GitHub'a yüklenmemelidir.
Her geliştirici kendi yerel PostgreSQL
veritabanını kullanmalıdır.