
# Akran Mentörlük Sistemi - API Sözleşmesi

## 1. Genel Bilgiler

Backend adresi: http://localhost:8000

Veri formatı: JSON

Kimlik doğrulama gerektiren endpoint'lerde JWT,
Authorization başlığı ile iletilir:

Authorization: Bearer <access_token>

Bu doküman Faz 3 geliştirme sürecindeki ortak API
sözleşmelerini tanımlar. Endpoint'lerin uygulanma durumu
ilgili geliştiricilerin Pull Request'leri üzerinden takip edilir.

## 2. Ortak Ders Modeli

| Alan | JSON tipi | Açıklama |
|---|---|---|
| id | integer | Benzersiz ders kimliği |
| code | string | Benzersiz ders kodu |
| name | string | Ders adı |
| description | string veya null | İsteğe bağlı açıklama |

### Benzersizlik Kuralları

- id benzersizdir.
- code benzersiz ve zorunludur.
- name zorunludur ancak benzersiz değildir.
- Farklı ders kodlarına sahip aynı isimli derslere izin verilir.
- Ders ilişkilerinde course_id kullanılmalıdır.

## 3. Ders Kataloğu

### GET /courses

Amaç: Sistemde bulunan ders kataloğunu listelemek.

Başarılı yanıt: HTTP 200 OK

Örnek yanıt:

```json
[
  {
    "id": 1,
    "code": "BYM308",
    "name": "Yapay Zekaya Giriş",
    "description": null
  },
  {
    "id": 2,
    "code": "BYM447",
    "name": "Makine Öğrenmesi",
    "description": null
  }
]
```

Örnekteki id değerleri temsilidir.

Ders bulunmadığında boş JSON dizisi döndürülür:

```json
[]
```

## 4. Mentör Profili ve Ders İlişkileri

Mentörün ders ekleme işlemlerinde ders adı yerine course_id
kullanılmalıdır.

Bir mentör aynı course_id değerini birden fazla kez ekleyemez.

Mentör profili yanıtlarında ders bilgisi sunulurken id,
code ve name alanları korunmalıdır.

## 5. Mentör Arama Uyumluluğu

Mentör arama işlemlerinde ders adı arama kriteri olarak
kullanılabilir.

Ancak aynı ders adına sahip farklı ders kayıtları bulunabileceği
için sonuçlarda ders kodu ve ders kimliği de bulunmalıdır.

## 6. Frontend Uyumluluk Kuralları

- Ders seçimlerinde id veya code kullanılmalıdır.
- Ders adının benzersiz olduğu varsayılmamalıdır.
- Ders kodu ve ders adı birlikte gösterilebilir.
- description alanının null olabileceği dikkate alınmalıdır.
- Mentör profili ve arama ekranları aynı ders modelini kullanmalıdır.

## 7. Değişiklik Yönetimi

Ortak API sözleşmesinde yapılan değişiklikler ilgili frontend,
backend ve test sorumlularıyla paylaşılmalıdır.

API alan adları veya veri tipleri koordinasyon olmadan
değiştirilmemelidir.

## 8. Kimlik Doğrulama ve Yetkilendirme

| Metot | Endpoint | Başarı kodu | Yetkilendirme |
|---|---|---|---|
| POST | /auth/register | 201 | Gerekmez |
| POST | /auth/login | 200 | Gerekmez |
| GET | /auth/me | 200 | JWT |
| POST | /mentors/profile | 201 | Doğrulanmış kullanıcı |
| GET | /mentors/profile | 200 | Doğrulanmış kullanıcı |
| GET | /courses | 200 | Doğrulanmış kullanıcı |
| POST | /mentors/courses | 201 | Doğrulanmış kullanıcı |
| GET | /mentors/search | 200 | Doğrulanmış kullanıcı |

Korumalı endpoint'lerde kullanıcı kimliği JWT üzerinden belirlenir. Kullanıcı kimliği istemciden alınmaz.

Yeni kayıt olan kullanıcılar doğrulanmamış durumdadır. Doğrulanmamış kullanıcı giriş yapabilir ancak doğrulama gerektiren işlemlerde 403 yanıtı alır.

## 9. Kayıt ve Giriş API'leri

### POST /auth/register

İstek:

```json
{
  "full_name": "Ayşe Yılmaz",
  "email": "ayse@ornek.edu.tr",
  "password": "EXAMPLE_PASSWORD"
}
```

Başarılı yanıt: HTTP 201 Created

```json
{
  "id": 1,
  "full_name": "Ayşe Yılmaz",
  "email": "ayse@ornek.edu.tr",
  "is_verified": false
}
```

### POST /auth/login

İstek:

```json
{
  "email": "ayse@ornek.edu.tr",
  "password": "EXAMPLE_PASSWORD"
}
```

Başarılı yanıt: HTTP 200 OK

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### GET /auth/me

Giriş yapan kullanıcının bilgilerini almak için kullanılır.

Geçerli JWT gerektirir. Güncel yanıt şeması auth router ve Swagger üzerinden takip edilir.

Parola veya parola hash bilgisi API yanıtlarında paylaşılmaz.

## 10. Mentör Profili Oluşturma

### POST /mentors/profile

İstek:

```json
{
  "bio": "Python ve programlama derslerinde yardımcı olabilirim.",
  "department": "Yazılım Mühendisliği"
}
```

Başarılı yanıt: HTTP 201 Created

```json
{
  "id": 1,
  "user_id": 1,
  "bio": "Python ve programlama derslerinde yardımcı olabilirim.",
  "department": "Yazılım Mühendisliği",
  "courses": []
}
```

Doğrulama kuralları:

- bio: 1–500 karakter.
- department: 2–100 karakter.
- Başlangıç ve bitiş boşlukları temizlenir.
- Her kullanıcı en fazla bir mentör profili oluşturabilir.
- Mükerrer profil oluşturma isteği 409 döndürür.
- Geçersiz giriş verileri 422 döndürür.

## 11. Mentör Profili Görüntüleme

### GET /mentors/profile

Giriş yapan kullanıcının kendi mentör profilini döndürür.

Başarılı yanıt: HTTP 200 OK

```json
{
  "id": 1,
  "user_id": 1,
  "bio": "Python ve programlama derslerinde yardımcı olabilirim.",
  "department": "Yazılım Mühendisliği",
  "courses": [
    {
      "id": 29,
      "code": "BIL302",
      "name": "İşletim Sistemleri"
    }
  ]
}
```

Kullanıcının mentör profili yoksa 404 döndürülür.

## 12. Mentör Profiline Ders Ekleme

### POST /mentors/courses

İstek:

```json
{
  "course_id": 29
}
```

Başarılı yanıt: HTTP 201 Created

```json
{
  "id": 1,
  "mentor_id": 1,
  "course_id": 29
}
```

Doğrulama kuralları:

- course_id pozitif bir tam sayı olmalıdır.
- Ders, veritabanında bulunmalıdır.
- Kullanıcının mentör profili bulunmalıdır.
- Aynı ders aynı profile ikinci kez eklenemez.
- mentor_id, kullanıcı kimliğini değil mentör profili kimliğini ifade eder.
- Kullanıcı yalnızca kendi profiline ders ekleyebilir.

## 13. Mentör Arama API Sözleşmesi

### GET /mentors/search?course_name=Matematik

Planlanan başarılı yanıt: HTTP 200 OK

```json
[
  {
    "mentor_id": 1,
    "full_name": "Ayşe Yılmaz",
    "department": "Yazılım Mühendisliği",
    "bio": "Matematik derslerinde yardımcı olabilirim.",
    "courses": [
      {
        "id": 1,
        "code": "MAT101",
        "name": "Matematik"
      }
    ]
  }
]
```

Arama kuralları:

- course_name boş olamaz ve en fazla 100 karakter olabilir.
- Büyük/küçük harf duyarsız kısmi eşleşme yapılır.
- Kullanıcının kendi mentör profili sonuçlara dahil edilmez.
- Doğrulanmamış kullanıcıların profilleri listelenmez.
- Aynı mentör sonuçlarda tekrarlanmaz.
- Sonuç bulunmadığında boş JSON dizisi döndürülür.

Bu bölüm Faz 3 ortak arama sözleşmesini tanımlar. Yusuf'un geliştirmesi tamamlandığında gerçek API yanıtlarıyla uyumluluğu doğrulanacaktır.

## 14. Ortak HTTP Durum Kodları

| Kod | Açıklama |
|---|---|
| 200 | Başarılı sorgulama veya giriş |
| 201 | Başarılı kayıt oluşturma |
| 401 | Eksik/geçersiz token veya hatalı giriş |
| 403 | Doğrulanmamış veya yetkisiz kullanıcı |
| 404 | Profil veya ders bulunamadı |
| 409 | Mükerrer kayıt |
| 422 | Geçersiz giriş verisi |

Standart hata yanıtı:

```json
{
  "detail": "Hata açıklaması"
}
```

422 doğrulama hatalarında detail alanı hata nesnelerinden oluşan bir liste olabilir.

Frontend uygulaması hata durumlarını uygun kullanıcı mesajlarıyla göstermelidir.

## 15. Faz 3 Entegrasyon Durumu

Mentör profili ve ders API'leri Swagger üzerinden pozitif ve negatif senaryolarla doğrulanmıştır.

Kimlik doğrulama, profil sahipliği, mükerrer kayıt, olmayan ders ve geçersiz veri kontrolleri test edilmiştir.

Arama API'si ve gerçek frontend entegrasyonu, ilgili ekip üyelerinin geliştirmeleri tamamlandıktan sonra yeniden doğrulanacaktır.

Bu dokümandaki örnek kimlikler ve ders kodları temsilidir.