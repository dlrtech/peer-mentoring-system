
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