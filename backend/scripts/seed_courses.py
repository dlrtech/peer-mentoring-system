
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Course


COURSES = [
    # 1. Yarıyıl
    ("ATA101", "Atatürk İlkeleri ve İnkılap Tarihi I"),
    ("BYM101", "Bilgisayar Programlama I"),
    ("FIZ101", "Fizik I"),
    ("ING101", "Temel İngilizce I"),
    ("MAT101", "Matematik I"),
    ("TRD101", "Türk Dili I"),
    ("YAZ101", "Yazılım Mühendisliğine Giriş"),

    # 2. Yarıyıl
    ("ATA102", "Atatürk İlkeleri ve İnkılap Tarihi II"),
    ("BIL104", "Mühendislik Tarihi"),
    ("BYM102", "Bilgisayar Programlama II"),
    ("FIZ102", "Fizik II"),
    ("ING102", "Temel İngilizce II"),
    ("KRY102", "Kariyer Planlama"),
    ("MAT102", "Matematik II"),
    ("TRD102", "Türk Dili II"),

    # 3. Yarıyıl
    ("BYM201", "Nesne Yönelimli Programlama"),
    ("ISG201", "İş Sağlığı ve Güvenliği I"),
    ("MAT201", "Lineer Cebir"),
    ("MAT205", "Ayrık Matematik"),
    ("YAZ213", "İnsan Bilgisayar Etkileşimi"),
    ("BYM402", "Programlama Dillerinin Prensipleri"),
    ("BYM445", "Görüntü İşleme"),
    ("BYM494", "Veri İletişimi"),

    # 4. Yarıyıl
    ("BYM202", "Veri Yapıları ve Algoritmalar"),
    ("ISG202", "İş Sağlığı ve Güvenliği II"),
    ("MAT202", "Sayısal Analiz"),
    ("YAZ208", "Hesaplama Sistemleri"),
    ("YAZ210", "Sistem Analizi ve Tasarımı"),
    ("BIL302", "İşletim Sistemleri"),
    ("BYM308", "Yapay Zekaya Giriş"),

    # 5. Yarıyıl
    ("BYM301", "Veritabanı Yönetimi"),
    ("BYM303", "Algoritma Analizi"),
    ("MAT301", "Olasılık ve İstatistik"),
    ("YAZ305", "Yazılım Proje Yönetimi"),
    ("YAZ309", "Staj I"),

    # 6. Yarıyıl
    ("BYM304", "Yazılım Mimarisi ve Tasarımı"),
    ("YAZ302", "Sistem Programlama"),
    ("YAZ308", "Yazılım Güvenliği"),
    ("ENM202", "Yöneylem Araştırması I"),
    ("MEK411", "Endüstriyel Otomasyon II"),

    # 7. Yarıyıl
    ("YAZ401", "Yazılım Kalite Standartları"),
    ("YAZ403", "Araştırma Çalışması"),
    ("YAZ405", "Staj II"),

    # Bölüm seçmeli dersleri
    ("BYM401", "Üretken AI"),
    ("BYM403", "Yazılım Geliştirme için İş Süreç Modelleme"),
    ("BYM404", "Endüstriyel Yapay Zekaya Giriş"),
    ("BYM405", "Graf Teorisine Giriş"),
    ("BYM406", "Siber Güvenlik"),
    ("BYM407", "Yeşil Bilişim"),
    ("BYM408", "Görsel Programlama"),
    ("BYM409", "Mobil Programlama"),
    ("BYM410", "Görüntü İşleme"),
    ("BYM411", "Veri Madenciliğine Giriş"),
    ("BYM412", "Robotik"),
    ("BYM413", "Nesnelerin İnterneti"),
    ("BYM414", "Blokzincir Teknolojisi ve Uygulamaları"),
    ("BYM415", "Web Programlama"),
    ("BYM416", "Oyun Programlama"),
    ("BYM417", "Yazılım Mühendisliğinde Güncel Konular"),
    ("BYM444", "Veri Bilimine Giriş"),
    ("BYM447", "Makine Öğrenmesi"),
    ("BYM448", "Biçimsel Diller ve Otomata Teorisi"),
    ("BYM449", "Ağ Güvenliği"),
    ("BYM450", "Kriptoloji"),
    ("BYM452", "Doğal Dil İşleme"),
    ("BYM454", "Biyoenformatik"),
    ("BYM455", "Bulut Bilişim"),
    ("BYM456", "Büyük Veri"),
    ("BYM457", "Bulanık Mantık"),
    ("BYM458", "Yapay Sinir Ağları"),
    ("BYM459", "Dağıtık Sistemler"),
    ("BYM460", "Yazılım Kalitesi ve Testi"),
    ("BYM463", "E-ticaret"),
    ("BYM464", "Paralel Programlama"),
    ("BYM465", "Yazılım Arayüz Tasarımı"),
    ("BYM466", "Sayısal Görüntü İşlemeye Giriş"),
    ("BYM467", "Yazılım Güvenliği"),
    ("BYM468", "Kriptografi"),
    ("BYM469", "Linux Sistem Yönetimi ve Kabuk Programlama"),
    ("BYM470", "Biyomedikal İşaret İşleme"),
    ("BYM471", "Mühendislikte Yöneylem Araştırması"),
    ("BYM472", "Gerçek Zamanlı Bilgisayar Sistemleri"),
    ("BYM474", "Biyoenformatiğe giriş"),
    ("BYM475", "Çoklu Ortam Yazılımı Geliştirme"),
    ("BYM477", "3B Modelleme ve Animasyon"),
    ("BYM478", "Sağlık Bilişimi"),
    ("BYM479", "Medikal Görüntü İşlemeye Giriş"),
    ("BYM480", "Makine Öğrenmesine Giriş"),
    ("BYM481", "Biyometrik Tanıma Sistemleri"),
    ("BYM482", "Derleyici Tasarımı"),
    ("BYM483", "Blokzincir Teknolojileri"),
    ("BYM484", "Sosyal Ağ Analizi"),
    ("BYM485", "Sanal Gerçeklik"),
    ("BYM486", "Sayısal Video İşlemeye Giriş"),
    ("BYM487", "Derin Öğrenmeye Giriş"),
    ("BYM488", "Sağlıkta Bilgisayar Teknolojileri ve Yazılım"),
    ("BYM489", "Örüntü Tanımaya Giriş"),
    ("BYM490", "Dağıtık Veritabanı Sistemleri"),
    ("BYM498", "Kriptografiye Giriş"),

    # 8. Yarıyıl
    ("GRS402", "Girişimcilik"),
    ("YAZ402", "Yazılım Gerçekleme, Test ve Bakım"),
    ("YAZ404", "Bitirme Çalışması"),
]


def seed_courses():
    db = SessionLocal()
    added_count = 0

    try:
        for code, name in COURSES:
            existing_course = db.scalar(
                select(Course).where(Course.code == code)
            )

            if existing_course is None:
                course = Course(
                    code=code,
                    name=name
                )

                db.add(course)
                added_count += 1
            else:
                existing_course.name = name

        db.commit()

        print(f"{added_count} yeni ders eklendi.")
        print(f"Katalogdaki toplam ders sayısı: {len(COURSES)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_courses()
