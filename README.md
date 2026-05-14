# Turkish Historical Research MCP Server

An MCP (Model Context Protocol) server that provides AI agents with structured access to three major Turkish historical research databases. Built for integration with LLM-based applications such as Claude Desktop to enable source-backed historical inquiry with automatic citation.

---

## Data Sources

### 1. Official Gazette of the Republic of Turkey (Resmi Gazete)

The official publication organ of the Turkish state, continuously archiving legislative and regulatory documents since 1921. The archive contains:
- Laws, decree-laws, and presidential decrees
- Regulations, communiques, and circulars
- Appointment decisions and public procurement notices
- Ratifications of international treaties

**Coverage:** 1921 -- present | **Source:** [resmigazete.gov.tr](https://www.resmigazete.gov.tr)

### 2. Belleten -- Journal of the Turkish Historical Society

Turkey's longest-running peer-reviewed academic history journal, published by the Turkish Historical Society (Turk Tarih Kurumu) since 1937. The journal includes:

- Scholarly articles on Turkish and world history
- Archaeological, art-historical, and philological research
- Biographical studies and social history analyses
- Full-text access to thousands of academic papers

**Coverage:** 1937 -- present | **Source:** [belleten.gov.tr](https://belleten.gov.tr)

### 3. TTK Digital Photograph Archive

The Turkish Historical Society's digitized visual collection spanning the late Ottoman period through the early Republic. The archive holds:

- Historical photographs of public figures, events, and locations
- Engravings, maps, and document reproductions
- Visual records from the War of Independence and the founding of the Republic

**Coverage:** Late Ottoman -- Early Republican era | **Source:** [arsiv.ttk.gov.tr](https://arsiv.ttk.gov.tr)

---

## Available Tools

| Tool | Function | Output |
|---|---|---|
| `resmiGazeteAra` | Keyword search in the Official Gazette archive | Document title, type, law number, date, issue number, URL |
| `belletenAra` | Multi-parameter academic article search in Belleten | 5 articles per page with title, author, DOI, full-text URL |
| `belletenOku` | Full-text retrieval of a specific Belleten article | Article metadata + body text (capped at 8000 chars) |
| `tarihiGorselAra` | Keyword search in the TTK photograph archive | Image titles, detail page URLs, direct image links |

All tool outputs include a source attribution line at the end for proper citation in generated responses.

---

## Project Structure

```
tr_tarih_agent/
├── main.py                          # Entry point (starts the MCP server)
├── requirements.txt                 # Python dependencies
├── .gitignore
├── README.md
└── server/
    ├── __init__.py                  # FastMCP server instance
    ├── prompts.py                   # All instructions and tool descriptions (single source of truth)
    ├── utils.py                     # Shared utilities: HTTP client, HTML parser, URL resolver
    └── tools/
        ├── __init__.py              # Tool registration and imports
        ├── resmi_gazete.py          # Official Gazette search implementation
        ├── belleten.py              # Belleten search + full-text reader implementation
        └── ttk_arsiv.py             # TTK photograph archive search implementation
```

**Architecture note:** All system instructions and tool descriptions are centralized in `server/prompts.py`. Each tool module imports its description from this single file, making prompt management and iteration straightforward.

---

## Installation

```bash
git clone https://github.com/momererkoc/tr_tarih_agent.git
cd tr_tarih_agent
pip install -r requirements.txt
```

## Usage

### Standalone

```bash
python main.py
```

### Claude Desktop Integration

Add the following entry to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "tr-tarih": {
      "command": "python",
      "args": ["/absolute/path/to/tr_tarih_agent/main.py"]
    }
  }
}
```

After restarting Claude Desktop, the four tools will be available for use in conversations.

---

## Citation Policy

The server is designed to support responsible use of historical sources. Every tool response includes structured source metadata, and the system instructions direct the consuming LLM to cite all sources used in its answers.

**Citation formats enforced by the system:**

| Source Type | Format |
|---|---|
| Belleten article | `(Source: Author, "Article Title", Belleten, DOI: ...)` |
| Official Gazette | `(Source: Resmi Gazete, Date, Issue: ...)` |
| TTK Archive | `(Source: TTK Digital Photograph Archive, arsiv.ttk.gov.tr)` |

---

## Requirements

- Python 3.10+
- `requests` >= 2.28.0
- `beautifulsoup4` >= 4.12.0
- `mcp[cli]` >= 1.0.0

## License

This project is provided for academic and research purposes. All data is retrieved in real time from publicly accessible government and institutional platforms. The project does not store, cache, or redistribute any copyrighted content.
