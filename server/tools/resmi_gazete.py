import requests
from server import mcp
from server.prompts import RESMI_GAZETE_DESC
from server.utils import fetch, clean_html


@mcp.tool(description=RESMI_GAZETE_DESC)
def resmiGazeteAra(anahtar: str) -> str:
    """
    Args:
        anahtar: 1-3 kelimelik anahtar kelime. Örnekler: "soyadı kanunu", "Lozan", "iş kanunu"
    """
    url = "https://www.resmigazete.gov.tr/Home/Filter"

    payload = {
        "draw": 1,
        "columns": [
            {"data": None, "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
            {"data": "kanunKararNo", "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
            {"data": "resmiGazeteTarihiFormatted", "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
            {"data": "resmiGazeteSayisi", "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
            {"data": None, "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}}
        ],
        "order": [],
        "start": 0,
        "length": 10,
        "search": {"value": "", "regex": False},
        "parameters": {
            "searchtype": "1",
            "genelaranacakkelime": anahtar,
            "genelbaslangictarihi": "1921-01-01",
            "genelbitistarihi": "2025-01-01",
            "genelsayi": "",
            "genelmevzuatsayisi": "",
            "genelmukerrer": "",
            "genelmevzuatturu": "",
            "genelkurumkodu": ""
        }
    }

    try:
        response = fetch(url, method="POST", headers={"Content-Type": "application/json"}, json_body=payload)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        return "Hata: Resmi Gazete sunucusu yanıt vermedi (zaman aşımı)."
    except requests.exceptions.RequestException as e:
        return f"Hata: Bağlantı sorunu - {e}"
    except Exception:
        return "Hata: Yanıt okunamadı."

    records = data.get("data", [])
    total = data.get("recordsTotal", 0)

    if not records:
        return f'"{anahtar}" için sonuç bulunamadı.'

    lines = [f'"{anahtar}" araması - {total} sonuç bulundu, ilk {len(records)} gösteriliyor:\n']

    for i, r in enumerate(records, 1):
        konu = clean_html(r.get("konu", "").strip())
        tarih = r.get("resmiGazeteTarihiFormatted", "")
        sayi = r.get("resmiGazeteSayisi", "")
        kanun_no = r.get("kanunKararNo", "")
        mevzuat = r.get("mevzuatAdi", "")
        fihrist = r.get("fihpiristUrl", "")
        url_val = f"https://www.resmigazete.gov.tr{fihrist}" if fihrist else ""

        lines.append(f"{i}. {konu}")
        if mevzuat:
            lines.append(f"   Tür: {mevzuat}")
        if kanun_no:
            lines.append(f"   No: {kanun_no}")
        lines.append(f"   Tarih: {tarih}, Sayı: {sayi}")
        if url_val:
            lines.append(f"   URL: {url_val}")
        lines.append("")

    lines.append("Kaynak: T.C. Resmi Gazete, resmigazete.gov.tr")

    return "\n".join(lines)
