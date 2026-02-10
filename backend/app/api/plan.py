from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models import Plan90Days, PlanStatus, User
from app.services.plan_generator import generate_plan_90_days

router = APIRouter(tags=["plan"])

DEFAULT_USER_ID = 1


class PlanGenerateRequest(BaseModel):
    context: dict[str, Any]
    chosen_option: str


class PlanGenerateResponse(BaseModel):
    plan_id: int
    status: PlanStatus
    plan: dict[str, Any]


def _validate_request(payload: PlanGenerateRequest) -> None:
    if not payload.context:
        raise HTTPException(status_code=400, detail="`context` doit être renseigné.")

    if not payload.chosen_option.strip():
        raise HTTPException(status_code=400, detail="`chosen_option` doit être renseigné.")


@router.post("/plan/generate", response_model=PlanGenerateResponse)
def generate_plan(
    payload: PlanGenerateRequest,
    session: Session = Depends(get_session),
) -> PlanGenerateResponse:
    _validate_request(payload)

    user = session.get(User, DEFAULT_USER_ID)
    if user is None:
        session.add(User(id=DEFAULT_USER_ID))
        session.flush()

    plan_payload = generate_plan_90_days(payload.context, payload.chosen_option)

    draft_plan = Plan90Days(
        user_id=DEFAULT_USER_ID,
        status=PlanStatus.draft,
        plan_json=plan_payload,
    )

    session.add(draft_plan)
    session.commit()
    session.refresh(draft_plan)

    return PlanGenerateResponse(
        plan_id=draft_plan.id or 0,
        status=draft_plan.status,
        plan=plan_payload,
    )
