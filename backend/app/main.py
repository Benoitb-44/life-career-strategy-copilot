from fastapi import FastAPI

from app.core.config import settings
from app.db import create_db_and_tables

app = FastAPI(title="Life Career Strategy Copilot API")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> dict[str, str]:
    _ = settings
    return {"status": "ok"}
