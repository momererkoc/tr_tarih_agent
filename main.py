import requests
import json
from bs4 import BeautifulSoup

from langchain.tools import tool

@tool("resmi_gazete_arama", description="Resmi Gazete'de belirli bir anahtar kelime ile arama yapar ve sonuçları döner.")
def resmi_gazete_arama(genelaranacakkelime : str) -> str:
    url = 'https://www.resmigazete.gov.tr/Home/Filter'

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
            "genelaranacakkelime": genelaranacakkelime,
            "genelbaslangictarihi": "1921-01-01",
            "genelbitistarihi": "2025-01-01",
            "genelsayi": "",
            "genelmevzuatsayisi": "",
            "genelmukerrer": "",
            "genelmevzuatturu": "",
            "genelkurumkodu": ""
        }
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    
    print(json.dumps(data, indent=4, ensure_ascii=False))

    return data

@tool("ttk_resim_arsivi", description="Türkiye Tarih Kurumu Resim Arşivi'nde belirli bir anahtar kelime ile arama yapar ve sonuçları döner.")
def ttk_resim_arsivi(query: str, max_results: int = 3):
    base_url = "https://arsiv.ttk.gov.tr"
    search_url = f"{base_url}/search?field=&mode=normal&query={query}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Arama sayfası hatası: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    search_divs = soup.find_all("div", class_="search-results")[:max_results]

    for div in search_divs:
        a_tag = div.find("a", class_="link-details")
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        href = a_tag.get("href")
        full_url = f"{base_url}{href}"

        
        detail_resp = requests.get(full_url, headers=headers)
        images = []
        if detail_resp.status_code == 200:
            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
            for img_a in detail_soup.find_all("a", class_="detail-image-link"):
                img_href = img_a.get("href")
                if img_href:
                    
                    img_url = f"{base_url}{img_href}"
                    images.append(img_url)

        results.append({
            "title": title,
            "images": images
        })

    final_json = {
        "query": query,
        "count": len(results),
        "results": results
    }

    print(json.dumps(final_json, indent=4, ensure_ascii=False))
    return final_json