from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from app.db import get_session
from app.models import CareerContext, User

router = APIRouter(tags=["context"])

DEFAULT_USER_ID = 1


class CareerContextUpsertRequest(BaseModel):
    primary_goal: str
    success_definition: str
    constraints: dict[str, Any]
    horizon_days: int | None = None


class CareerContextResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    primary_goal: str
    success_definition: str
    constraints: dict[str, Any]
    horizon_days: int | None = None
    updated_at: datetime


def _validate_payload(payload: CareerContextUpsertRequest) -> None:
    errors: list[str] = []

    if not payload.primary_goal.strip():
        errors.append("`primary_goal` doit être renseigné.")

    if payload.horizon_days is not None and payload.horizon_days > 90:
        errors.append("`horizon_days` doit être inférieur ou égal à 90.")

    if not payload.success_definition.strip():
        errors.append("`success_definition` doit être renseigné.")

    if not payload.constraints:
        errors.append("`constraints` doit contenir au moins une contrainte.")

    if errors:
        raise HTTPException(status_code=400, detail=errors)


@router.post("/context", response_model=CareerContextResponse)
def upsert_context(
    payload: CareerContextUpsertRequest,
    session: Session = Depends(get_session),
) -> CareerContext:
    _validate_payload(payload)

    user = session.get(User, DEFAULT_USER_ID)
    if user is None:
        session.add(User(id=DEFAULT_USER_ID))
        session.flush()

    context = session.get(CareerContext, DEFAULT_USER_ID)
    now = datetime.now(timezone.utc)

    if context is None:
        context = CareerContext(
            user_id=DEFAULT_USER_ID,
            primary_goal=payload.primary_goal.strip(),
            success_definition=payload.success_definition.strip(),
            constraints=payload.constraints,
            horizon_days=payload.horizon_days,
            updated_at=now,
        )
    else:
        context.primary_goal = payload.primary_goal.strip()
        context.success_definition = payload.success_definition.strip()
        context.constraints = payload.constraints
        context.horizon_days = payload.horizon_days
        context.updated_at = now

    session.add(context)
    session.commit()
    session.refresh(context)
    return context


@router.get("/context", response_model=CareerContextResponse)
def get_context(session: Session = Depends(get_session)) -> CareerContext:
    context = session.get(CareerContext, DEFAULT_USER_ID)
    if context is None:
        raise HTTPException(status_code=404, detail="CareerContext introuvable.")
    return context

