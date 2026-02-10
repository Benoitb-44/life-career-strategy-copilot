from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models import ChecklistResult, Plan90Days, PlanStatus, User
from app.services.checklist import evaluate_plan_checklist
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


class PlanEvaluateResponse(BaseModel):
    plan_id: int
    status: PlanStatus
    checklist_result_id: int
    verdict: str
    feedback: str


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


@router.post("/plan/{plan_id}/evaluate", response_model=PlanEvaluateResponse)
def evaluate_plan(
    plan_id: int,
    session: Session = Depends(get_session),
) -> PlanEvaluateResponse:
    plan = session.get(Plan90Days, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan introuvable.")

    result = evaluate_plan_checklist(plan.plan_json)

    checklist_result = ChecklistResult(
        plan_id=plan_id,
        clarity=result.clarity,
        focus=result.focus,
        actionability=result.actionability,
        feasibility=result.feasibility,
        risk_awareness=result.risk_awareness,
        coherence=result.coherence,
        verdict=result.verdict,
        feedback=result.feedback,
    )

    plan.status = PlanStatus.approved if result.verdict == "approved" else PlanStatus.rejected

    session.add(checklist_result)
    session.add(plan)
    session.commit()
    session.refresh(checklist_result)
    session.refresh(plan)

    return PlanEvaluateResponse(
        plan_id=plan.id or 0,
        status=plan.status,
        checklist_result_id=checklist_result.id or 0,
        verdict=checklist_result.verdict,
        feedback=checklist_result.feedback,
    )
