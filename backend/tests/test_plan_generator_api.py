import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine, select

from app.api.plan import PlanGenerateRequest, evaluate_plan, generate_plan
from app.models import ChecklistResult, Plan90Days, PlanStatus
from app.services.plan_generator import (
    FORBIDDEN_DELIVERABLE_TERMS,
    _contains_forbidden_terms,
    generate_plan_90_days,
)


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def _build_payload() -> PlanGenerateRequest:
    return PlanGenerateRequest(
        context={
            "primary_goal": "Décrocher un poste data",
            "success_definition": "Avoir 3 entretiens qualifiés",
            "constraints": {"temps": "8h/semaine"},
            "horizon_days": 90,
        },
        chosen_option="Trajectoire équilibrée",
    )


def test_generate_plan_90_days_schema_and_forbidden_words() -> None:
    plan = generate_plan_90_days(
        context={"primary_goal": "Lancer une activité freelance", "success_definition": "Signer 2 clients"},
        chosen_option="Trajectoire offensive",
    )

    assert set(plan.keys()) == {"objective", "monthly_objectives", "kpis", "risks"}
    assert len(plan["monthly_objectives"]) == 3

    for month in plan["monthly_objectives"]:
        assert set(month.keys()) == {"month", "objective", "deliverables"}
        assert isinstance(month["deliverables"], list)
        assert len(month["deliverables"]) >= 1

        for deliverable in month["deliverables"]:
            assert not _contains_forbidden_terms(deliverable)
            assert not any(term in deliverable.casefold() for term in FORBIDDEN_DELIVERABLE_TERMS)


def test_generate_plan_requires_payload_values(session: Session) -> None:
    request = PlanGenerateRequest(context={}, chosen_option="  ")

    with pytest.raises(HTTPException) as exc_info:
        generate_plan(request, session)

    assert exc_info.value.status_code == 400


def test_generate_plan_persists_draft_plan(session: Session) -> None:
    request = _build_payload()

    response = generate_plan(request, session)

    assert response.plan_id > 0
    assert response.status == PlanStatus.draft
    assert set(response.plan.keys()) == {"objective", "monthly_objectives", "kpis", "risks"}

    plans = session.exec(select(Plan90Days)).all()
    assert len(plans) == 1

    stored = plans[0]
    assert stored.status == PlanStatus.draft
    assert set(stored.plan_json.keys()) == {"objective", "monthly_objectives", "kpis", "risks"}
    assert len(stored.plan_json["monthly_objectives"]) == 3


def test_evaluate_plan_rejects_bad_plan_and_persists_checklist(session: Session) -> None:
    bad_plan = Plan90Days(
        user_id=1,
        status=PlanStatus.draft,
        plan_json={
            "objective": "Trouver mieux",
            "monthly_objectives": [{"month": 1, "objective": "vite", "deliverables": []}],
            "kpis": [],
            "risks": [],
        },
    )
    session.add(bad_plan)
    session.commit()
    session.refresh(bad_plan)

    response = evaluate_plan(bad_plan.id or 0, session)

    assert response.verdict == "rejected"
    assert response.status == PlanStatus.rejected
    assert response.checklist_result_id > 0

    stored_plan = session.get(Plan90Days, bad_plan.id)
    assert stored_plan is not None
    assert stored_plan.status == PlanStatus.rejected

    checklist_results = session.exec(select(ChecklistResult)).all()
    assert len(checklist_results) == 1
    checklist = checklist_results[0]
    assert checklist.verdict == "rejected"
    assert not checklist.clarity
    assert not checklist.coherence
    assert "Plan rejeté" in checklist.feedback


def test_evaluate_plan_never_returns_partial_verdict(session: Session) -> None:
    request = _build_payload()
    generated = generate_plan(request, session)

    response = evaluate_plan(generated.plan_id, session)

    assert response.verdict in {"approved", "rejected"}
    assert response.verdict != "partial"
