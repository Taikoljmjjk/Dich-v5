
import os, re, shutil, tempfile
from pathlib import Path
from urllib.parse import urlparse, quote

import yt_dlp
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

app = FastAPI(title="TÀI LÊ MMO Multi Downloader V5", version="5.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["GET", "OPTIONS"], allow_headers=["*"]
)

STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

def validate_url(url: str):
    try:
        p = urlparse(url.strip())
        if p.scheme not in ("http", "https") or not p.netloc:
            raise ValueError()
        return url.strip()
    except Exception:
        raise HTTPException(400, "URL không hợp lệ.")

def platform_name(url: str):
    h = urlparse(url).netloc.lower().replace("www.", "")
    if "facebook.com" in h or "fb.watch" in h: return "Facebook"
    if "tiktok.com" in h: return "TikTok"
    if "youtube.com" in h or "youtu.be" in h: return "YouTube"
    if "instagram.com" in h: return "Instagram"
    if h in ("x.com","twitter.com") or "twitter.com" in h: return "X / Twitter"
    if "reddit.com" in h or "redd.it" in h: return "Reddit"
    if "vimeo.com" in h: return "Vimeo"
    return h or "Website"

def clean_info(info, url):
    thumbs = info.get("thumbnails") or []
    thumbnail = info.get("thumbnail") or (thumbs[-1].get("url") if thumbs else "")
    formats = info.get("formats") or []
    heights = sorted({int(f["height"]) for f in formats if f.get("height")}, reverse=True)
    qualities = [h for h in heights if h <= 2160][:8]
    if not qualities:
        qualities = [1080,720,480,360]
    return {
        "ok": True,
        "platform": platform_name(url),
        "title": info.get("title") or "Video",
        "uploader": info.get("uploader") or info.get("channel") or "",
        "duration": info.get("duration"),
        "thumbnail": thumbnail,
        "webpage_url": info.get("webpage_url") or url,
        "qualities": qualities,
        "is_playlist": bool(info.get("_type") == "playlist" or info.get("entries")),
    }

@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")

@app.get("/api/health")
def health():
    return {"ok": True, "version": "5.0"}

@app.get("/api/info")
def info(url: str = Query(...)):
    url = validate_url(url)
    opts = {
        "quiet": True, "no_warnings": True, "skip_download": True,
        "noplaylist": True, "socket_timeout": 20,
        "http_headers": {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36"}
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
        return clean_info(data, url)
    except Exception as e:
        msg = str(e)
        if len(msg) > 420: msg = msg[-420:]
        raise HTTPException(400, f"Không phân tích được liên kết. {msg}")

def remove_tree(path):
    shutil.rmtree(path, ignore_errors=True)

@app.get("/api/download")
def download(url: str = Query(...), height: int = Query(720, ge=144, le=2160), audio: bool = False):
    url = validate_url(url)
    td = tempfile.mkdtemp(prefix="taile_v5_")
    outtmpl = os.path.join(td, "%(title).120B [%(id)s].%(ext)s")
    opts = {
        "outtmpl": outtmpl,
        "quiet": True, "no_warnings": True, "noplaylist": True,
        "socket_timeout": 30,
        "windowsfilenames": True,
        "http_headers": {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36"},
    }
    if audio:
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}],
        })
    else:
        opts.update({
            "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best",
            "merge_output_format": "mp4",
        })
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
        files = [p for p in Path(td).iterdir() if p.is_file() and not p.name.endswith((".part",".ytdl"))]
        if not files:
            raise RuntimeError("Không tìm thấy file sau khi tải.")
        f = max(files, key=lambda p: p.stat().st_mtime)
        media = "audio/mpeg" if f.suffix.lower()==".mp3" else "application/octet-stream"
        return FileResponse(
            f, filename=f.name, media_type=media,
            background=BackgroundTask(remove_tree, td)
        )
    except Exception as e:
        remove_tree(td)
        msg = str(e)
        if len(msg) > 500: msg = msg[-500:]
        raise HTTPException(400, f"Tải thất bại. {msg}")
