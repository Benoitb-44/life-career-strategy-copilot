import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine, select

from app.api.plan import PlanGenerateRequest, generate_plan
from app.models import Plan90Days, PlanStatus
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
