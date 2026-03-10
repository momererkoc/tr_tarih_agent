"""
Tüm MCP tool açıklamaları ve sistem talimatları bu dosyada toplanır.
Başka modüller buradan import ederek kullanır.
"""

SERVER_INSTRUCTIONS = """4 araç var. DOĞRU ARACI SEÇ, rastgele deneme:

belletenAra -> Tarihi bir konu, kişi, olay, dönem hakkında BİLGİ istendiğinde KULLAN. Bu en sık kullanacağın araç.
belletenOku -> belletenAra sonucundan seçtiğin makalenin tam metnini okumak için kullan.
resmiGazeteAra -> SADECE kanun, yönetmelik, kararname gibi MEVZUAT sorulduğunda kullan. Kişiler, olaylar, tarih bilgisi için KULLANMA.
tarihiGorselAra -> SADECE fotoğraf, resim, görsel istendiğinde kullan.

KARAR ŞEMASI:
- "Atatürk'ün mal varlığı" -> belletenAra (kişi hakkında bilgi = akademik makale)
- "Osmanlı'da vakıf sistemi" -> belletenAra (tarih konusu = akademik makale)
- "Soyadı Kanunu ne zaman çıktı?" -> resmiGazeteAra (kanun = mevzuat)
- "Lozan Antlaşması metni" -> resmiGazeteAra (antlaşma metni = resmi belge)
- "Atatürk fotoğrafları" -> tarihiGorselAra (fotoğraf = görsel)
- "Kurtuluş Savaşı'nda İngilizlerin rolü" -> belletenAra (analiz = akademik makale)

KULLANIM AKIŞI:
1. belletenAra ile ara, 5 makale döner
2. Başlıklara bak, soruya EN ALAKALI olanı seç (ilk makaleyi körü körüne seçme)
3. Seçtiğin makalenin URL'sini belletenOku'ya ver
4. Okuduğun bilgiyle kullanıcıya cevap ver

ANAHTAR KELİME: 1-3 kelime yaz, soru cümlesi yazma. "Atatürk'ün mal varlığı hakkında bilgi ver" -> "mal varlığı" olarak ara.

ATIF: Cevabında kaynağı mutlaka belirt. Her araç çıktısının sonunda kaynak satırı var, onu kullan."""


RESMI_GAZETE_DESC = (
    "T.C. Resmi Gazete arşivinde SADECE mevzuat arar: kanun, yönetmelik, kararname, tebliğ (1921-2025). "
    "Tarihi bilgi, kişi biyografisi, olay analizi için bu aracı KULLANMA, onlar için belletenAra kullan. "
    "1-3 kelimelik kısa anahtar kelime gir. Örnek: 'soyadı kanunu', 'iş kanunu', 'Lozan'."
)

BELLETEN_ARA_DESC = (
    "TTK Belleten dergisinde akademik tarih makalesi arar. "
    "Bir kişi, olay, dönem veya konu hakkında bilgi istendiğinde İLK bu aracı kullan. "
    "Resmi Gazete değil, burası doğru kaynak: biyografi, savaş, toplum, ekonomi, kültür gibi tarih konuları burada. "
    "5 sonuç döner, daha fazla istersen sayfaNo artır."
)

BELLETEN_OKU_DESC = (
    "Belleten makalesinin tam metnini okur. "
    "Önce belletenAra ile arama yap, dönen sonuçlardan en alakalı makalenin URL'sini buraya ver."
)

TARIHI_GORSEL_DESC = (
    "TTK dijital fotoğraf arşivinde tarihi görsel arar. "
    "SADECE kullanıcı fotoğraf, resim veya görsel istediğinde kullan. "
    "Yazılı bilgi için bu aracı kullanma, belletenAra kullan. "
    "1-2 kelimelik kısa anahtar kelime gir. Örnek: 'Atatürk', 'Çanakkale'."
)
