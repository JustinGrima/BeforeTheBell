from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import configure_logging

configure_logging()
app = FastAPI(title="BeforeTheBell")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
