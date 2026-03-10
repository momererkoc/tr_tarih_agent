class Config:
    # URL'ler
    RESMI_GAZETE_URL = "https://www.resmigazete.gov.tr/Home/Filter"
    BELLETEN_URL = "https://belleten.gov.tr"
    TTK_ARSIV_URL = "https://arsiv.ttk.gov.tr"
    TBMM_MAZBATA_GET_URL = "https://www.tbmm.gov.tr/Kutuphane/MazbataArama"
    TBMM_MAZBATA_POST_URL = "https://www.tbmm.gov.tr/Kutuphane/MazbataAramaSonuc"

    # User-Agent ve Headers
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    DEFAULT_HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }

    # Sınırlar
    MAX_ARTICLE_CHARS = 8000
    MAX_SEARCH_RESULTS = 5
