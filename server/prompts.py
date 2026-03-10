"""
Tüm MCP tool açıklamaları ve sistem talimatları bu dosyada toplanır.
Başka modüller buradan import ederek kullanır.
"""

SERVER_INSTRUCTIONS = """3 araç var:

1. resmiGazeteAra: Kanun, yönetmelik, kararname gibi resmi devlet belgelerini arar. Akademik bilgi için KULLANMA.
2. belletenAra + belletenOku: Tarih konularında akademik makale arar ve okur. Tarihi sorularda İLK bu aracı kullan. Arama 5 makale döner, başlıklara bakıp en alakalı makaleyi seç ve belletenOku ile oku.
3. tarihiGorselAra: Tarihi fotoğraf/görsel arar.

Anahtar kelime kuralları: 1-3 kelime yaz, soru cümlesi yazma. "Atatürk'ün mal varlığı hakkında bilgi ver" -> "mal varlığı" olarak ara.

ATIF KURALI: Kullanıcıya cevap verirken, bilgiyi aldığın kaynağa mutlaka atıf yap. Her araçtan dönen çıktının sonunda kaynak bilgisi bulunur, bunu kullan. Örnek atıf formatları:
- Belleten makalesi: (Kaynak: Yazar Adı, "Makale Başlığı", Belleten, DOI: ...)
- Resmi Gazete: (Kaynak: Resmi Gazete, Tarih, Sayı: ...)
- TTK Arşiv: (Kaynak: TTK Dijital Fotoğraf Arşivi, arsiv.ttk.gov.tr)"""


# Tool açıklamaları

RESMI_GAZETE_DESC = (
    "T.C. Resmi Gazete arşivinde kanun, yönetmelik, kararname gibi "
    "resmi belgeleri arar (1921-2025). 1-3 kelimelik kısa anahtar kelime gir."
)

BELLETEN_ARA_DESC = (
    "TTK Belleten dergisinde akademik tarih makalesi arar. "
    "Tarihle ilgili her soruda ilk bunu kullan. "
    "5 sonuç döner, daha fazla istersen sayfaNo artır."
)

BELLETEN_OKU_DESC = (
    "Belleten makalesinin tam metnini okur. "
    "belletenAra sonucundaki URL'yi ver."
)

TARIHI_GORSEL_DESC = (
    "TTK dijital fotoğraf arşivinde tarihi görsel arar. "
    "1-2 kelimelik kısa anahtar kelime gir."
)
