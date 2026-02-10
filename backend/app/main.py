from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title="Life Career Strategy Copilot API")


@app.get("/health")
def health() -> dict[str, str]:
    _ = settings
    return {"status": "ok"}
