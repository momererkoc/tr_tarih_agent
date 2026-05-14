import os
import json
import asyncio
import time
from collections import defaultdict
from typing import AsyncGenerator

import anthropic
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.tools.resmi_gazete import resmi_gazete_tool
from server.tools.belleten import belleten_tool
from server.tools.ttk_arsiv import ttk_arsiv_tool
from server.tools.tbmm import tbmm_tool
from server.prompts import SERVER_INSTRUCTIONS

app = FastAPI(title="Türkiye Tarih Araştırma Ajanı")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    base_url="https://token-plan-sgp.xiaomimimo.com/anthropic",
)

# ── Rate limiting ─────────────────────────────
RATE_LIMIT  = 10     # max requests
RATE_WINDOW = 3600   # per hour (seconds)
_rate_store: dict[str, list[float]] = defaultdict(list)

def check_rate_limit(ip: str) -> tuple[bool, int, int]:
    """Returns (allowed, used, remaining_seconds)."""
    now = time.time()
    window_start = now - RATE_WINDOW
    timestamps = [t for t in _rate_store[ip] if t > window_start]
    _rate_store[ip] = timestamps
    if len(timestamps) >= RATE_LIMIT:
        reset_in = int(RATE_WINDOW - (now - timestamps[0]))
        return False, len(timestamps), reset_in
    _rate_store[ip].append(now)
    return True, len(_rate_store[ip]), 0

# ── Tools ─────────────────────────────────────
TOOLS = [
    {
        "name": "resmiGazeteAra",
        "description": "Resmi Mevzuat: Kanun, kararname ve resmi ilanların metinlerini arar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "anahtar": {"type": "string", "description": "Aranacak anahtar kelime"}
            },
            "required": ["anahtar"]
        }
    },
    {
        "name": "belletenAra",
        "description": "Akademik Literatür: TTK Belleten dergisinde yayınlanan bilimsel tarih makalelerini arar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "baslik":  {"type": "string",  "description": "Makale başlığı"},
                "yazar":   {"type": "string",  "description": "Yazar adı"},
                "anahtar": {"type": "string",  "description": "Anahtar kelime"},
                "sayfaNo": {"type": "integer", "description": "Sayfa numarası", "default": 1}
            }
        }
    },
    {
        "name": "belletenOku",
        "description": "Akademik Literatür: Seçilen bilimsel makalenin tam metnini okur.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Makale URL'si"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "tarihiGorselAra",
        "description": "Görsel Arşiv: Tarihi fotoğraf ve resimleri TTK arşivinde arar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query":     {"type": "string",  "description": "Arama sorgusu"},
                "maxSonuc":  {"type": "integer", "description": "Maksimum sonuç sayısı", "default": 3}
            },
            "required": ["query"]
        }
    },
    {
        "name": "mazbataAra",
        "description": "TBMM Arşiv Kaydı: Milletvekillerinin şahsi tercüme-i hallerini ve seçim mazbatalarını arar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "adi":    {"type": "string", "description": "Milletvekilinin adı"},
                "soyadi": {"type": "string", "description": "Milletvekilinin soyadı"}
            }
        }
    }
]

TOOL_META = {
    "resmiGazeteAra":  {"label": "Resmi Gazete", "abbr": "RG", "color": "#3b82f6"},
    "belletenAra":     {"label": "Belleten",      "abbr": "BL", "color": "#8b5cf6"},
    "belletenOku":     {"label": "Makale Oku",    "abbr": "MO", "color": "#6d28d9"},
    "tarihiGorselAra": {"label": "Görsel Arşiv",  "abbr": "GA", "color": "#10b981"},
    "mazbataAra":      {"label": "TBMM Arşivi",   "abbr": "TB", "color": "#f59e0b"},
}

DEFAULT_MODEL = "mimo-v2.5"


def run_tool(name: str, inputs: dict) -> str:
    try:
        if name == "resmiGazeteAra":
            return resmi_gazete_tool.ara(inputs["anahtar"])
        elif name == "belletenAra":
            return belleten_tool.ara(
                baslik=inputs.get("baslik", ""),
                yazar=inputs.get("yazar", ""),
                anahtar=inputs.get("anahtar", ""),
                sayfaNo=inputs.get("sayfaNo", 1),
            )
        elif name == "belletenOku":
            return belleten_tool.oku(inputs["url"])
        elif name == "tarihiGorselAra":
            return ttk_arsiv_tool.ara(inputs["query"], inputs.get("maxSonuc", 3))
        elif name == "mazbataAra":
            return tbmm_tool.mazbataAra(inputs.get("adi", ""), inputs.get("soyadi", ""))
        return "Bilinmeyen araç."
    except Exception as e:
        return f"Araç hatası: {e}"


class ChatRequest(BaseModel):
    query: str
    model: str = DEFAULT_MODEL


async def stream_chat(query: str, model: str) -> AsyncGenerator[str, None]:
    loop = asyncio.get_event_loop()
    # Fresh context every request — no history
    history = [{"role": "user", "content": query}]

    while True:
        response = await loop.run_in_executor(
            None,
            lambda h=history: client.messages.create(
                model=model,
                max_tokens=4096,
                system=SERVER_INSTRUCTIONS,
                tools=TOOLS,
                messages=h,
            )
        )

        tool_calls = []

        for block in response.content:
            if block.type == "text":
                yield f"data: {json.dumps({'type': 'text', 'text': block.text})}\n\n"
            elif block.type == "tool_use":
                meta = TOOL_META.get(block.name, {"label": block.name, "abbr": "??", "color": "#6b7280"})
                tool_calls.append({"id": block.id, "name": block.name, "input": block.input, "meta": meta})
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': block.name, 'input': block.input, 'meta': meta})}\n\n"

        if response.stop_reason == "tool_use":
            history.append({"role": "assistant", "content": response.content})
            tool_results = []
            for tc in tool_calls:
                result = await loop.run_in_executor(None, lambda t=tc: run_tool(t["name"], t["input"]))
                tool_results.append({"type": "tool_result", "tool_use_id": tc["id"], "content": result})
                yield f"data: {json.dumps({'type': 'tool_result', 'tool': tc['name'], 'result': result[:600], 'meta': tc['meta']})}\n\n"
            history.append({"role": "user", "content": tool_results})
            continue

        break

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    ip = request.client.host or "unknown"
    allowed, used, reset_in = check_rate_limit(ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limited",
                "message": f"Saatte en fazla {RATE_LIMIT} soru sorabilirsiniz.",
                "reset_in": reset_in,
            }
        )
    return StreamingResponse(
        stream_chat(req.query, req.model or DEFAULT_MODEL),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-RateLimit-Limit": str(RATE_LIMIT),
            "X-RateLimit-Used": str(used),
            "X-RateLimit-Remaining": str(max(0, RATE_LIMIT - used)),
        }
    )


@app.get("/api/rate-status")
async def rate_status(request: Request):
    ip = request.client.host or "unknown"
    now = time.time()
    timestamps = [t for t in _rate_store[ip] if t > now - RATE_WINDOW]
    used = len(timestamps)
    reset_in = int(RATE_WINDOW - (now - timestamps[0])) if timestamps else 0
    return {
        "limit": RATE_LIMIT,
        "used": used,
        "remaining": max(0, RATE_LIMIT - used),
        "reset_in": reset_in,
    }


@app.get("/api/tools")
def get_tools():
    return [
        {**t, "meta": TOOL_META.get(t["name"], {"label": t["name"], "abbr": "??", "color": "#6b7280"})}
        for t in TOOLS
    ]


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
