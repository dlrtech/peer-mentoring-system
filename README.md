# Akran Mentörlük Sistemi

Üniversite öğrencilerinin ders verebildiği ve başka derslerde destek alabildiği,
tarayıcıda çalışan tek bir web uygulaması. Yazılım Kalite dersi proje çalışmasıdır.

## Temel kural

- Her öğrenci **tek hesapla** hem mentor hem mentee olabilir. Kayıtta kalıcı rol seçimi yoktur.
- Ders vermek isteyen öğrenci bir **mentor profili** oluşturur.
- Öğrenci kendi profilini arama sonuçlarında görmez.
- Admin yetkisi ayrıdır; istemciden verilemez.

## Teknolojiler

| Katman | Teknoloji |
|---|---|
| Frontend | React, Vite, React Router |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| Veritabanı | PostgreSQL |
| Güvenlik | Argon2id parola hash'i, JWT |
| Test | Pytest |

## Hızlı başlangıç

Önkoşullar: Python 3.12, Node.js 20.19+ (veya 22.12+), PostgreSQL.

Ayrıntılar için: [backend/README.md](backend/README.md) ve [frontend/README.md](frontend/README.md).

**1. Backend** (`backend/` klasöründe, boş bir `akran_mentorluk` veritabanı açıldıktan sonra)

```bash
python -m venv .venv
python -m pip install -r requirements.txt
cp .env.example .env          # DATABASE_URL ve SECRET_KEY'i kendinize göre düzenleyin
python -m alembic upgrade head
python -m scripts.seed_courses
python -m uvicorn app.main:app --reload
```

Windows'ta sanal ortam için `.\.venv\Scripts\Activate.ps1`, kopyalama için `Copy-Item .env.example .env` kullanın.

- Swagger: http://localhost:8000/docs
- Sağlık kontrolü: http://localhost:8000/health

**2. Frontend** (`frontend/` klasöründe)

```bash
npm ci
cp .env.example .env
npm run dev
```

Uygulama: http://localhost:5173

**3. Testler** (`backend/` klasöründe)

```bash
python -m pytest tests/unit
```

`tests/integration` canlı PostgreSQL veritabanına bağlanır; önce migration ve seed çalıştırılmış olmalıdır.

> `.env` dosyaları ve gerçek parolalar GitHub'a yüklenmez; yalnızca `.env.example` paylaşılır.
> Her geliştirici kendi yerel PostgreSQL veritabanını kullanır.

## Proje durumu (Faz 3)

| API | Durum |
|---|---|
| `POST /auth/register`, `POST /auth/login` | Hazır |
| `GET /auth/me` | İnceleme bekliyor |
| `GET /courses`, `POST /mentors/profile`, `GET /mentors/profile`, `POST /mentors/courses` | Yapılacak |
| `GET /mentors/search` | Yapılacak |

Yeni kayıtlar doğrulanmamış (`is_verified=false`) açılır; e-posta doğrulaması Faz 4'e bırakılmıştır.
Bu tablo geliştirme ilerledikçe güncellenir.

## Klasör yapısı

```
backend/    FastAPI uygulaması, modeller, migration'lar, testler
frontend/   React uygulaması
docs/       Mimari, API sözleşmesi ve karar kayıtları
```

## Dokümanlar

- [Sistem mimarisi](docs/architecture.md)
- [API sözleşmesi](docs/api-contract.md)

## Git iş akışı

- `main`: test edilmiş, demo için hazır kod. Doğrudan push yapılmaz.
- `develop`: ortak entegrasyon branch'i. Tüm Pull Request'ler buraya açılır.
- `setup/*`: geçici altyapı branch'leri. `feature/<ad>-<konu>`: kişisel geliştirme branch'leri.
- Her değişiklik Pull Request ile girer; en az bir kişi inceler, bulgular aynı branch'e yeni commit olarak işlenir.

```bash
git switch develop
git pull origin develop
git switch -c feature/<kendi-branch-adi>
# çalış, test et
git add <dosya-yolu>
git commit -m "Açıklayıcı bir mesaj"
git push -u origin feature/<kendi-branch-adi>
```

## Ekip

| Üye | Sorumluluk (Faz 3) |
|---|---|
| Dilara Kılıç | Proje yönetimi, kayıt/giriş |
| Tuğba Korkut | Mimari, veritabanı, profil ve ders API'leri |
| Yusuf Deligöz | Mentor arama |
| Berat Serçe | Frontend altyapısı, kayıt/giriş ekranları |
| Miraç Arda Seçkin | Profil ve arama ekranları |
| Hilal Zeynep Karaca | Test altyapısı ve testler |
| Mert Mak | Kimlik ve parola güvenliği |
