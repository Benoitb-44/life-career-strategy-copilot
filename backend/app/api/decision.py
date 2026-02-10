from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models import CareerContext, Decision, User
from app.services.decision_engine import check_constraints, force_tradeoff, generate_options

router = APIRouter(tags=["decision"])

DEFAULT_USER_ID = 1


class DecisionOption(BaseModel):
    title: str
    value: str
    effort: str
    risk: str


class ConstraintCheckResponse(BaseModel):
    ok: bool
    issue: str
    suggested_adjustment: str | None = None


class DecisionOptionsResponse(BaseModel):
    constraint_check: ConstraintCheckResponse
    options: list[DecisionOption]


class DecisionChooseRequest(BaseModel):
    options: list[str]
    chosen_option: str
    abandoned_options: list[str]
    justification: str


class DecisionChooseResponse(BaseModel):
    decision_id: int
    validated: bool
    chosen_option: str
    abandoned_options: list[str]
    justification: str


@router.post("/decision/options", response_model=DecisionOptionsResponse)
def decision_options(session: Session = Depends(get_session)) -> DecisionOptionsResponse:
    context = session.get(CareerContext, DEFAULT_USER_ID)
    if context is None:
        raise HTTPException(status_code=404, detail="CareerContext introuvable.")

    payload = {
        "primary_goal": context.primary_goal,
        "success_definition": context.success_definition,
        "constraints": context.constraints,
        "horizon_days": context.horizon_days,
    }

    constraint_check = check_constraints(payload)
    if not constraint_check["ok"]:
        raise HTTPException(status_code=400, detail=constraint_check)

    options_payload = generate_options(payload)
    return DecisionOptionsResponse(
        constraint_check=ConstraintCheckResponse(**constraint_check),
        options=[DecisionOption(**option) for option in options_payload["options"]],
    )


@router.post("/decision/choose", response_model=DecisionChooseResponse)
def decision_choose(
    request: DecisionChooseRequest,
    session: Session = Depends(get_session),
) -> DecisionChooseResponse:
    if len(request.options) > 3:
        raise HTTPException(status_code=400, detail="Le nombre d'options ne peut pas dépasser 3.")

    if not request.justification.strip():
        raise HTTPException(status_code=400, detail="Impossible de choisir sans justification.")

    if request.chosen_option not in request.options:
        raise HTTPException(status_code=400, detail="`chosen_option` doit appartenir à `options`.")

    if set(request.abandoned_options) - set(request.options):
        raise HTTPException(status_code=400, detail="`abandoned_options` doit être un sous-ensemble de `options`.")

    user = session.get(User, DEFAULT_USER_ID)
    if user is None:
        session.add(User(id=DEFAULT_USER_ID))
        session.flush()

    try:
        validated = force_tradeoff(
            chosen=request.chosen_option,
            justification=request.justification,
            abandoned=request.abandoned_options,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    decision = Decision(
        user_id=DEFAULT_USER_ID,
        options=request.options,
        chosen_option=request.chosen_option,
        abandoned_options=request.abandoned_options,
        justification=request.justification.strip(),
    )
    session.add(decision)
    session.commit()
    session.refresh(decision)

    return DecisionChooseResponse(
        decision_id=decision.id or 0,
        validated=bool(validated["validated"]),
        chosen_option=validated["chosen_option"],
        abandoned_options=validated["abandoned_options"],
        justification=validated["justification"],
    )
