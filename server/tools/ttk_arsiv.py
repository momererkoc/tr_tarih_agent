import requests
from server import mcp
from server.prompts import TARIHI_GORSEL_DESC
from server.utils import fetch, parse_html, fix_relative_url


BASE_URL = "https://arsiv.ttk.gov.tr"


@mcp.tool(description=TARIHI_GORSEL_DESC)
def tarihiGorselAra(query: str, maxSonuc: int = 3) -> str:
    """
    Args:
        query: 1-2 kelimelik anahtar kelime. Örnekler: "Atatürk", "Çanakkale", "Ankara"
        maxSonuc: Maksimum sonuç sayısı (varsayılan 3)
    """
    try:
        response = fetch(f"{BASE_URL}/search", params={"field": "", "mode": "normal", "query": query})
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return "Hata: TTK arşiv sunucusu yanıt vermedi."
    except requests.exceptions.RequestException as e:
        return f"Hata: Bağlantı sorunu - {e}"

    soup = parse_html(response.text)
    results = []

    for div in soup.find_all("div", class_="search-results")[:maxSonuc]:
        a_tag = div.find("a", class_="link-details")
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        detail_url = fix_relative_url(BASE_URL, a_tag.get("href", ""))

        images = []
        try:
            detail_resp = fetch(detail_url)
            if detail_resp.status_code == 200:
                detail_soup = parse_html(detail_resp.text)
                for img_a in detail_soup.find_all("a", class_="detail-image-link"):
                    img_href = img_a.get("href", "")
                    if img_href:
                        images.append(fix_relative_url(BASE_URL, img_href))
        except requests.exceptions.RequestException:
            pass

        results.append({"title": title, "detail_url": detail_url, "images": images})

    if not results:
        return f'"{query}" için görsel bulunamadı.'

    lines = [f'"{query}" araması - {len(results)} sonuç:\n']
    for i, r in enumerate(results, 1):
        lines.append(f'{i}. {r["title"]}')
        lines.append(f'   Detay: {r["detail_url"]}')
        if r["images"]:
            for img in r["images"]:
                lines.append(f'   Görsel: {img}')
        else:
            lines.append('   (Görsel bulunamadı)')
        lines.append("")

    lines.append("Kaynak: TTK Dijital Fotoğraf Arşivi, arsiv.ttk.gov.tr")

    return "\n".join(lines)
