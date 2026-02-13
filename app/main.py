from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.logging import configure_logging

configure_logging()
app = FastAPI(title="CoverCall AI")
app.include_router(router)

WEB_DIR = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


@app.get("/")
def home():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
