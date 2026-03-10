from server import mcp
from server.config import Config
from server.utils import HttpClient, clean_html
from server.prompts import RESMI_GAZETE_DESC


class ResmiGazeteTool:
    def __init__(self):
        self.http = HttpClient()

    def ara(self, anahtar: str) -> str:
        payload = {
            "draw": 1,
            "columns": [{"data": "konu"}, {"data": "kanunKararNo"}, {"data": "resmiGazeteTarihiFormatted"}, {"data": "resmiGazeteSayisi"}],
            "start": 0,
            "length": 10,
            "parameters": {
                "searchtype": "1",
                "genelaranacakkelime": anahtar,
                "genelbaslangictarihi": "1921-01-01",
                "genelbitistarihi": "2025-01-01"
            }
        }
        try:
            resp = self.http.fetch(Config.RESMI_GAZETE_URL, method="POST", json_body=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return f"Hata: Resmi Gazete bağlantı sorunu - {e}"

        records = data.get("data", [])
        if not records:
            return "Sonuç bulunamadı."

        lines = [f'Resmi Gazete Araması ("{anahtar}") - {len(records)} sonuç:\n']
        for i, r in enumerate(records, 1):
            konu = clean_html(r.get("konu", ""))
            tarih = r.get("resmiGazeteTarihiFormatted", "")
            sayi = r.get("resmiGazeteSayisi", "")
            fihrist = r.get("fihpiristUrl", "")
            url = f"https://www.resmigazete.gov.tr{fihrist}" if fihrist else "URL Bulunamadı"

            lines.append(f"{i}. {konu}")
            lines.append(f"   KAYNAK: Resmi Gazete, Tarih: {tarih}, Sayı: {sayi}")
            lines.append(f"   BELGE URL: {url}")
            lines.append("")

        return "\n".join(lines)


resmi_gazete_tool = ResmiGazeteTool()

@mcp.tool(description=RESMI_GAZETE_DESC)
def resmiGazeteAra(anahtar: str) -> str:
    return resmi_gazete_tool.ara(anahtar)
