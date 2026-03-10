import requests
from server import mcp
from server.prompts import BELLETEN_ARA_DESC, BELLETEN_OKU_DESC
from server.utils import fetch, parse_html


BASE_URL = "https://belleten.gov.tr"
MAX_ARTICLE_CHARS = 8000


@mcp.tool(description=BELLETEN_ARA_DESC)
def belletenAra(
    baslik: str = "",
    yazar: str = "",
    anahtar: str = "",
    ozet: str = "",
    tamMetin: str = "",
    yil: str = "",
    cilt: str = "",
    sayfaNo: int = 1
) -> str:
    """
    Args:
        baslik: Başlıkta aranacak kelime. Örnek: "Kurtuluş Savaşı"
        yazar: Yazar adı/soyadı. Örnek: "İnalcık"
        anahtar: Konu anahtar kelimesi. Örnek: "mal varlığı", "vakıf"
        ozet: Özette aranacak ifade
        tamMetin: Tüm metinde aranacak ifade (geniş kapsamlı)
        yil: Yayın yılı. Örnek: "2020"
        cilt: Cilt numarası. Örnek: "88"
        sayfaNo: Sonuç sayfası (her sayfada 5 makale). Daha fazla sonuç için artır.
    """
    params = {
        "title": baslik,
        "authors": yazar,
        "affiliations": "",
        "keywords": anahtar,
        "abstract": ozet,
        "body": tamMetin,
        "year": yil,
        "volume": cilt,
        "first_page": "",
        "doi": ""
    }

    try:
        req_params = dict(params)
        if sayfaNo > 1:
            req_params["page"] = str(sayfaNo)
        resp = fetch(
            f"{BASE_URL}/arama-sonuclari",
            params=req_params,
            headers={"Referer": f"{BASE_URL}/arama"}
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return "Hata: Belleten sunucusu yanıt vermedi."
    except requests.exceptions.RequestException as e:
        return f"Hata: Bağlantı sorunu - {e}"

    soup = parse_html(resp.text)

    toplam_sayfa = _parse_pagination(soup)
    articles = _parse_articles(soup)[:5]

    if not articles:
        return "Sonuç bulunamadı. Daha genel bir anahtar kelime dene."

    arama_terimi = baslik or anahtar or yazar or ozet or tamMetin or "genel"
    lines = [f'"{arama_terimi}" araması - sayfa {sayfaNo}/{toplam_sayfa} (5 makale, daha fazla için sayfaNo artır):\n']

    for i, art in enumerate(articles, 1):
        lines.append(f'{i}. {art["baslik"]}')
        lines.append(f'   Yazar: {art["yazarlar"]}')
        if art["doi"]:
            lines.append(f'   DOI: {art["doi"]}')
        lines.append(f'   Oku: {art["url"]}')
        lines.append("")

    lines.append("Kaynak: Belleten - Türk Tarih Kurumu Dergisi, belleten.gov.tr")

    return "\n".join(lines)


@mcp.tool(description=BELLETEN_OKU_DESC)
def belletenOku(url: str) -> str:
    """
    Args:
        url: Makalenin tam metin URL'si. Örnek: https://belleten.gov.tr/tam-metin/211/tur
    """
    try:
        response = fetch(url)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return "Hata: Sayfa yüklenemedi (zaman aşımı)."
    except requests.exceptions.RequestException as e:
        return f"Hata: Bağlantı sorunu - {e}"

    soup = parse_html(response.text)

    baslik, yazar, anahtar_kelimeler = _parse_article_meta(soup)
    tam_metin = _extract_full_text(soup)

    if not tam_metin and not baslik:
        return f"Makale içeriği okunamadı. URL'yi kontrol et: {url}"

    if len(tam_metin) > MAX_ARTICLE_CHARS:
        tam_metin = tam_metin[:MAX_ARTICLE_CHARS] + "\n\n[Metin çok uzun, ilk 8000 karakter gösterildi]"

    lines = [f"Başlık: {baslik}", f"Yazar: {yazar}"]
    if anahtar_kelimeler:
        lines.append(f"Anahtar Kelimeler: {anahtar_kelimeler}")
    lines.append(f"URL: {url}")
    lines.append("")
    lines.append(tam_metin)
    lines.append("")
    lines.append(f'Kaynak: {yazar}, "{baslik}", Belleten - Türk Tarih Kurumu Dergisi, belleten.gov.tr')

    return "\n".join(lines)


def _parse_pagination(soup) -> int:
    pagination = soup.find("div", class_="pagination")
    if not pagination:
        return 1

    last_link = pagination.find("a", string=">>")
    if last_link:
        href = last_link.get("href", "")
        if "page=" in href:
            try:
                return int(href.split("page=")[-1])
            except ValueError:
                pass

    page_numbers = []
    for li in pagination.find_all("li"):
        a = li.find("a")
        if a and a.get_text(strip=True).isdigit():
            page_numbers.append(int(a.get_text(strip=True)))

    return max(page_numbers) if page_numbers else 1


def _parse_articles(soup) -> list:
    articles = []
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        if not a_tag:
            continue

        title = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")
        tam_metin_url = f"{BASE_URL}{href}" if href else ""

        authors_p = h3.find_next_sibling("p")
        authors = authors_p.get_text(strip=True) if authors_p else ""

        article_div = h3.parent
        info_div = article_div.find("div", class_="span8") if article_div else None
        doi_val = ""
        if info_div:
            parts = info_div.get_text(separator="|", strip=True).split("|")
            for idx, part in enumerate(parts):
                if part.strip() == "DOI:" and idx + 1 < len(parts):
                    doi_val = parts[idx + 1].strip()

        articles.append({
            "baslik": title,
            "yazarlar": authors,
            "doi": doi_val,
            "url": tam_metin_url
        })

    return articles


def _parse_article_meta(soup) -> tuple:
    baslik = ""
    yazar = ""
    anahtar_kelimeler = ""

    article_meta = soup.find(id="article-meta")
    if article_meta:
        h1 = article_meta.find("h1")
        if h1:
            baslik = h1.get_text(strip=True)
        ps = article_meta.find_all("p")
        if len(ps) >= 1:
            yazar = ps[0].get_text(strip=True)
        if len(ps) >= 2:
            anahtar_kelimeler = ps[1].get_text(strip=True)

    return baslik, yazar, anahtar_kelimeler


def _extract_full_text(soup) -> str:
    wrapper = soup.find(id="wrapper")
    if wrapper:
        main = wrapper.find("main")
        if main:
            article = main.find("article")
            if article:
                return article.get_text(separator="\n", strip=True)
    return ""
