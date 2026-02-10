import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine, select

from app.api.bets import StrategicBetsRequest, create_bets
from app.models import Plan90Days, PlanStatus
from app.services.strategic_bets import generate_strategic_bets


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def _build_payload() -> StrategicBetsRequest:
    return StrategicBetsRequest(
        context={
            "primary_goal": "Décrocher un poste data",
            "success_definition": "Avoir 3 entretiens qualifiés",
            "constraints": {"temps": "8h/semaine"},
            "horizon_days": 90,
        },
        chosen_option="Trajectoire équilibrée",
    )


def test_generate_strategic_bets_is_stable_and_non_empty() -> None:
    context = {
        "primary_goal": "Lancer une activité freelance",
        "success_definition": "Signer 2 clients",
    }

    first = generate_strategic_bets(context, "Trajectoire offensive")
    second = generate_strategic_bets(context, "Trajectoire offensive")

    assert first == second
    assert len(first) >= 1
    assert all(set(bet.keys()) == {"hypothesis", "success_signal", "main_risk", "fallback"} for bet in first)


def test_create_bets_requires_payload_values(session: Session) -> None:
    request = StrategicBetsRequest(context={}, chosen_option="  ")

    with pytest.raises(HTTPException) as exc_info:
        create_bets(request, session)

    assert exc_info.value.status_code == 400


def test_create_bets_persists_draft_plan_json(session: Session) -> None:
    request = _build_payload()

    response = create_bets(request, session)

    assert response.plan_id > 0
    assert response.status == PlanStatus.draft
    assert isinstance(response.bets, list)
    assert len(response.bets) >= 1

    plans = session.exec(select(Plan90Days)).all()
    assert len(plans) == 1

    stored = plans[0]
    assert stored.status == PlanStatus.draft
    assert stored.plan_json["chosen_option"] == request.chosen_option
    assert stored.plan_json["context"] == request.context
    assert isinstance(stored.plan_json["bets"], list)
    assert len(stored.plan_json["bets"]) >= 1
