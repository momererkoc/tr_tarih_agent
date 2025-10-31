import requests
import json
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



