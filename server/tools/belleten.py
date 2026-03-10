from server import mcp
from server.config import Config
from server.utils import HttpClient, parse_html, clean_html
from server.prompts import BELLETEN_ARA_DESC, BELLETEN_OKU_DESC


class BelletenTool:
    def __init__(self):
        self.http = HttpClient()

    def ara(self, baslik: str = "", yazar: str = "", anahtar: str = "", sayfaNo: int = 1) -> str:
        params = {
            "title": baslik,
            "authors": yazar,
            "keywords": anahtar,
            "page": str(sayfaNo) if sayfaNo > 1 else ""
        }
        try:
            resp = self.http.fetch(f"{Config.BELLETEN_URL}/arama-sonuclari", params=params)
            resp.raise_for_status()
        except Exception as e:
            return f"Hata: Belleten bağlantı sorunu - {e}"

        soup = parse_html(resp.text)
        articles = self._parse_articles(soup)

        if not articles:
            return "Sonuç bulunamadı."

        lines = [f"Belleten Akademik Makale Araması - {len(articles)} sonuç:\n"]
        for i, art in enumerate(articles, 1):
            lines.append(f"{i}. {art['baslik']}")
            lines.append(f"   Yazar: {art['yazarlar']}")
            lines.append(f"   Kaynak: Belleten Dergisi, URL: {art['url']}")
            lines.append("")

        return "\n".join(lines)

    def oku(self, url: str) -> str:
        try:
            resp = self.http.fetch(url)
            resp.raise_for_status()
        except Exception as e:
            return f"Hata: Makale okunamadı - {e}"

        soup = parse_html(resp.text)
        content = self._extract_content(soup)
        
        if len(content) > Config.MAX_ARTICLE_CHARS:
            content = content[:Config.MAX_ARTICLE_CHARS] + "..."

        return f"{content}\n\nKAYNAKÇA: Belleten Dergisi, Makale URL: {url}"

    def _parse_articles(self, soup):
        articles = []
        for h3 in soup.find_all("h3")[:5]:
            a = h3.find("a")
            if not a: continue
            articles.append({
                "baslik": clean_html(a.get_text()),
                "url": f"{Config.BELLETEN_URL}{a.get('href', '')}",
                "yazarlar": clean_html(h3.find_next_sibling("p").get_text()) if h3.find_next_sibling("p") else "Belirtilmemiş",
            })
        return articles

    def _extract_content(self, soup):
        article = soup.find("article")
        return clean_html(article.get_text(separator="\n")) if article else "İçerik bulunamadı."


belleten_tool = BelletenTool()

@mcp.tool(description=BELLETEN_ARA_DESC)
def belletenAra(baslik: str = "", yazar: str = "", anahtar: str = "", sayfaNo: int = 1) -> str:
    return belleten_tool.ara(baslik, yazar, anahtar, sayfaNo)

@mcp.tool(description=BELLETEN_OKU_DESC)
def belletenOku(url: str) -> str:
    return belleten_tool.oku(url)
