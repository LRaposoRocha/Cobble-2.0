# python -m uvicorn cobble2_Backend:app --reload

import os
import re
import time
import shutil
import yt_dlp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

# ===================== FastAPI + CORS =====================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# ===================== Progresso de download =====================

progress_data = {}
last_sent     = {}

# ===================== Sanitização de nome =====================

def sanitize_filename(name):

    return re.sub(r'[\\/*?:"<>|]', "_", name)

# ===================== Rota de progresso =====================

@app.get("/progress")
async def progress_stream(url: str, format: str):

    def event_stream():

        while True:

            data = progress_data.get(url, {})
            now  = time.time()
            last = last_sent.get(url, 0)

            if now - last >= 1:
                yield f"data: {data}\n\n"
                last_sent[url] = now

            if data.get("status") == "done":
                break

            time.sleep(0.25)

    return StreamingResponse(event_stream(), media_type = "text/event-stream")

# ===================== Rota de download =====================

@app.get("/download")
async def download(request: Request, url: str, format: str):

    try:

        progress_data[url] = { "progress": 0, "status": "downloading" }

        temp_dir   = os.path.join(os.getcwd(), "temp")
        final_path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(temp_dir, exist_ok = True)

        ydl_opts = {
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "progress_hooks": [lambda d: update_progress(d, url)],
        }

        if format == "audio":

            ydl_opts.update({
                "format": "bestaudio",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }]
            })

        else:
            ydl_opts.update({
                # Tenta baixar o melhor mp4, se não conseguir, tenta qualquer outro
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download = True)

            title     = info.get("title", "video")
            ext       = "mp3" if format == "audio" else "mp4"
            file_name = f"{sanitize_filename(title)}.{ext}"
            file_path = os.path.join(temp_dir, file_name)
            dest_path = os.path.join(final_path, file_name)

            if not os.path.exists(file_path):
                raise FileNotFoundError("Arquivo final não encontrado após o download.")

            shutil.move(file_path, dest_path)

            now = time.time()
            os.utime(dest_path, (now, now))

        shutil.rmtree(temp_dir, ignore_errors = True)
        progress_data[url] = { "progress": 100, "status": "done" }

        return JSONResponse(content = { "message": "Download concluído." })

    except Exception as e:

        progress_data[url] = { "progress": 0, "status": "done" }

        return JSONResponse(status_code = 500, content = {
            "message": "Erro ao baixar o vídeo.",
            "error": str(e)
        })

# ===================== Hook de progresso =====================

def update_progress(d, url):

    if d["status"] == "downloading":

        downloaded = d.get("downloaded_bytes", 0)
        total      = d.get("total_bytes") or d.get("total_bytes_estimate")

        if total:

            percent = int(downloaded / total * 100)
            progress_data[url] = {
                "progress": percent,
                "status": "downloading"
            }
