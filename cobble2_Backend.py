import os, asyncio
from fastapi import FastAPI, WebSocket
from yt_dlp import YoutubeDL

app = FastAPI()

def make_hook(ws: WebSocket):
    def hook(d):
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
            downloaded = d.get('downloaded_bytes', 0)
            percent = downloaded / total * 100
            # agendar envio sem bloquear o hook
            asyncio.create_task(ws.send_json({
                "type": "progress",
                "percent": percent
            }))
    return hook

@app.websocket("/ws")
async def websocket_download(ws: WebSocket):
    await ws.accept()
    data = await ws.receive_json()
    url = data.get("url")
    fmt = data.get("format_type", "video")
    out = "downloads"
    os.makedirs(out, exist_ok=True)

    opts = {
        "format": "bestvideo+bestaudio/best" if fmt == "video" else "bestaudio",
        "outtmpl": os.path.join(out, "%(title)s.%(ext)s"),
        "progress_hooks": [make_hook(ws)]
    }
    if fmt == "audio":
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]

    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        await ws.send_json({"type": "complete", "message": "Download concluído."})
    except Exception as e:
        await ws.send_json({"type": "error", "message": str(e)})
    await ws.close()
