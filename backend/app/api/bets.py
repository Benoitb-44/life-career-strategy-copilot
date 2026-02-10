from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import Plan90Days, PlanStatus, User
from app.services.strategic_bets import generate_strategic_bets

router = APIRouter(tags=["bets"])

DEFAULT_USER_ID = 1


class StrategicBetsRequest(BaseModel):
    context: dict[str, Any]
    chosen_option: str


class StrategicBet(BaseModel):
    hypothesis: str
    success_signal: str
    main_risk: str
    fallback: str


class StrategicBetsResponse(BaseModel):
    plan_id: int
    status: PlanStatus
    bets: list[StrategicBet]


def _validate_request(payload: StrategicBetsRequest) -> None:
    if not payload.context:
        raise HTTPException(status_code=400, detail="`context` doit être renseigné.")

    if not payload.chosen_option.strip():
        raise HTTPException(status_code=400, detail="`chosen_option` doit être renseigné.")


@router.post("/bets", response_model=StrategicBetsResponse)
def create_bets(
    payload: StrategicBetsRequest,
    session: Session = Depends(get_session),
) -> StrategicBetsResponse:
    _validate_request(payload)

    user = session.get(User, DEFAULT_USER_ID)
    if user is None:
        session.add(User(id=DEFAULT_USER_ID))
        session.flush()

    bets_payload = generate_strategic_bets(payload.context, payload.chosen_option)
    if not bets_payload:
        raise HTTPException(status_code=500, detail="Impossible de générer des paris stratégiques.")

    draft_plan = session.exec(
        select(Plan90Days)
        .where(Plan90Days.user_id == DEFAULT_USER_ID)
        .where(Plan90Days.status == PlanStatus.draft)
        .order_by(Plan90Days.created_at.desc())
    ).first()

    plan_json = {
        "context": payload.context,
        "chosen_option": payload.chosen_option.strip(),
        "bets": bets_payload,
    }

    if draft_plan is None:
        draft_plan = Plan90Days(
            user_id=DEFAULT_USER_ID,
            status=PlanStatus.draft,
            plan_json=plan_json,
        )
    else:
        draft_plan.plan_json = plan_json

    session.add(draft_plan)
    session.commit()
    session.refresh(draft_plan)

    return StrategicBetsResponse(
        plan_id=draft_plan.id or 0,
        status=draft_plan.status,
        bets=[StrategicBet(**bet) for bet in bets_payload],
    )
