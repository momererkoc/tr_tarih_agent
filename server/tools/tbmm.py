from server import mcp
from server.config import Config
from server.utils import HttpClient, parse_html, clean_html, fix_relative_url
from server.prompts import TBMM_MAZBATA_DESC


class TbmmTool:
    """
    Yasama Organı Üyelerinin Tercüme-i Halleri ve Seçim Mazbataları Arama Aracı
    """
    def __init__(self):
        self.http = HttpClient()

    def _get_csrf_token(self):
        """TBMM sayfasından CSRF tokeni alır"""
        try:
            resp = self.http.fetch(Config.TBMM_MAZBATA_GET_URL)
            soup = parse_html(resp.text)
            token_input = soup.find("input", {"name": "X-CSRF-TOKEN-TBMM.WEB.Mvc.Prod"})
            return token_input["value"] if token_input else None
        except Exception:
            return None

    def mazbataAra(self, adi: str = "", soyadi: str = "") -> str:
        """
        Yasama organı üyelerinin hayat hikayesi ve mazbatasını arar.
        """
        token = self._get_csrf_token()
        if not token:
            return "Hata: TBMM oturumu başlatılamadı (CSRF Token bulunamadı)."

        payload = {
            "X-CSRF-TOKEN-TBMM.WEB.Mvc.Prod": token,
            "PageIndex": 0,
            "Adi": adi,
            "Soyadi": soyadi,
            "IlId": "",
            "DonemId": ""
        }

        try:
            resp = self.http.fetch(
                Config.TBMM_MAZBATA_POST_URL,
                method="POST",
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            resp.raise_for_status()
        except Exception as e:
            return f"Hata: TBMM sorgusu başarısız oldu - {e}"

        soup = parse_html(resp.text)
        results = self._parse_results(soup)

        if not results:
            return f'"{adi} {soyadi}" için kayıt bulunamadı.'

        lines = [f'"{adi} {soyadi}" araması için bulunan kayıtlar:\n']
        
        for i, res in enumerate(results, 1):
            lines.append(f"{i}. {res['ad_soyad']}")
            if res['gorev_detay']:
                lines.append(f"   Görev/Dönem: {res['gorev_detay']}")
            
            if res['pdf_links']:
                lines.append("   Belgeler:")
                for label, link in res['pdf_links'].items():
                    lines.append(f"     - {label}: {link}")
            lines.append("")

        lines.append("Kaynak: TBMM Kütüphane - Tercüme-i Hal ve Mazbata Arşivi, tbmm.gov.tr")
        return "\n".join(lines)

    def _parse_results(self, soup):
        results = []
        # Sonuçların toplandığı ana div
        sonuc_alani = soup.find(id="sonucAlani")
        if not sonuc_alani:
            return []

        # Her bir sonuç bloğu (genelde isim bazlı divler)
        # XPath'e göre: //*[@id="sonucAlani"]/div[1], div[2]...
        result_blocks = sonuc_alani.find_all("div", recursive=False)
        
        for block in result_blocks:
            # İsim ve Soyisim bilgisini çekmeye çalışalım
            # Genelde h4 veya benzeri bir başlıkta olur, ya da tablonun üstündeki divlerde
            name_tag = block.find(class_="isim_soyisim") or block.find("h4")
            ad_soyad = clean_html(name_tag.get_text()) if name_tag else "Bilinmeyen Üye"

            # Bu bloğun içindeki görev listesini ve tabloları bulalım
            pdf_links = {}
            gorev_bilgisi = ""

            tables = block.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if not cols:
                        continue
                    
                    # Görev metnini al (İlk kolon genelde görev/dönem adıdır)
                    row_text = clean_html(row.get_text(separator=" "))
                    
                    # PDF Linklerini bul (td[3]/a gibi spesifik hücrelerde veya tüm td'lerde)
                    links = row.find_all("a")
                    for a in links:
                        href = a.get("href", "")
                        if not href or href == "#":
                            continue
                        
                        full_url = fix_relative_url("https://www.tbmm.gov.tr", href)
                        link_text = clean_html(a.get_text()) or "Belge"
                        
                        # Eğer link metni çok kısaysa veya yoksa kolon başlığına göre isimlendir
                        if "TercumeiHal" in href:
                            label = f"Tercüme-i Hal ({link_text})"
                        elif "Mazbata" in href:
                            label = f"Mazbata ({link_text})"
                        else:
                            label = f"Ek Belge ({link_text})"
                        
                        # Benzersiz olması için URL'yi ekle
                        pdf_links[label] = full_url

            results.append({
                "ad_soyad": ad_soyad,
                "gorev_detay": None, # Tablo içinden toplu geliyor zaten
                "pdf_links": pdf_links
            })
            
        return results


# Singleton instance
tbmm_tool = TbmmTool()

@mcp.tool(description=TBMM_MAZBATA_DESC)
def mazbataAra(adi: str = "", soyadi: str = "") -> str:
    return tbmm_tool.mazbataAra(adi, soyadi)
