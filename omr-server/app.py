"""AnnApp sheet-music reader: photo(s) in, MusicXML out (homr, AGPL-3.0)."""
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

MAX_BYTES = 12 * 1024 * 1024
MAX_FILES = 4
TIMEOUT = 300
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["*"], max_age=86400)
busy = threading.Semaphore(1)


@app.get("/")
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "annapp-omr"}


@app.post("/api/convert")
def convert(files: list[UploadFile] = File(...)) -> Response:
    if not 1 <= len(files) <= MAX_FILES:
        raise HTTPException(400, f"Wyślij od 1 do {MAX_FILES} zdjęć.")
    if not busy.acquire(timeout=240):
        raise HTTPException(429, "Serwer jest zajęty. Spróbuj za chwilę.")
    work = Path(tempfile.mkdtemp(prefix="omr-"))
    try:
        paths = []
        for i, f in enumerate(files):
            body = f.file.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise HTTPException(413, "Zdjęcie jest za duże (najwyżej 12 MB).")
            ext = Path(f.filename or "").suffix.lower()
            p = work / f"page{i + 1}{ext if ext in EXTS else '.jpg'}"
            p.write_bytes(body)
            paths.append(str(p))
        try:
            run = subprocess.run([sys.executable, "-m", "homr.main", *paths], cwd=work,
                                 capture_output=True, text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "Odczyt trwał za długo.")
        out = sorted(work.glob("merged_*.musicxml")) or sorted(work.glob("*.musicxml"))
        if not out:
            print(run.stderr[-2000:], file=sys.stderr)
            raise HTTPException(422, "Nie udało się odczytać nut z tego zdjęcia.")
        return Response(out[0].read_bytes(), media_type="application/vnd.recordare.musicxml+xml")
    finally:
        busy.release()
        shutil.rmtree(work, ignore_errors=True)
