from fastapi import FastAPI

from app.core.config import settings
from app.api.context import router as context_router
from app.api.decision import router as decision_router
from app.api.bets import router as bets_router
from app.api.plan import router as plan_router
from app.db import create_db_and_tables

app = FastAPI(title="Life Career Strategy Copilot API")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> dict[str, str]:
    _ = settings
    return {"status": "ok"}


app.include_router(context_router)
app.include_router(decision_router)
app.include_router(bets_router)
app.include_router(plan_router)
