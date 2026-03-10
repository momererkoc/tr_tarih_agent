from server import mcp
from server.config import Config
from server.utils import HttpClient, parse_html, clean_html, fix_relative_url
from server.prompts import TARIHI_GORSEL_DESC


class TtkArsivTool:
    def __init__(self):
        self.http = HttpClient()

    def ara(self, query: str, maxSonuc: int = 3) -> str:
        try:
            resp = self.http.fetch(f"{Config.TTK_ARSIV_URL}/search", params={"query": query})
            resp.raise_for_status()
        except Exception as e:
            return f"Hata: TTK Arşiv bağlantı sorunu - {e}"

        soup = parse_html(resp.text)
        results = self._parse_results(soup, maxSonuc)

        if not results:
            return "Görsel bulunamadı."

        lines = [f'TTK Fotoğraf Arşivi ("{query}") - {len(results)} sonuç:\n']
        for i, res in enumerate(results, 1):
            lines.append(f"{i}. {res['title']}")
            for img in res['images']:
                lines.append(f"   Görsel URL: {img}")
            lines.append(f"   Kaynak: TTK Dijital Fotoğraf Arşivi, {Config.TTK_ARSIV_URL}")
            lines.append("")

        return "\n".join(lines)

    def _parse_results(self, soup, max_results):
        results = []
        for div in soup.find_all("div", class_="search-results")[:max_results]:
            a = div.find("a", class_="link-details")
            if not a: continue
            
            title = clean_html(a.get_text())
            detail_url = fix_relative_url(Config.TTK_ARSIV_URL, a.get("href", ""))
            
            images = []
            try:
                d_resp = self.http.fetch(detail_url)
                d_soup = parse_html(d_resp.text)
                for img_a in d_soup.find_all("a", class_="detail-image-link"):
                    images.append(fix_relative_url(Config.TTK_ARSIV_URL, img_a.get("href", "")))
            except: pass

            results.append({"title": title, "images": images})
        return results


ttk_arsiv_tool = TtkArsivTool()

@mcp.tool(description=TARIHI_GORSEL_DESC)
def tarihiGorselAra(query: str, maxSonuc: int = 3) -> str:
    return ttk_arsiv_tool.ara(query, maxSonuc)
