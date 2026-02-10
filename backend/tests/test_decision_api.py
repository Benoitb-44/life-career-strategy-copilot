import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine, select

from app.api.context import CareerContextUpsertRequest, upsert_context
from app.api.decision import DecisionChooseRequest, decision_choose, decision_options
from app.models import Decision
from app.services.decision_engine import check_constraints, force_tradeoff, generate_options


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def _seed_context(session: Session) -> None:
    payload = CareerContextUpsertRequest(
        primary_goal="Décrocher un poste data",
        success_definition="Signer une offre",
        constraints={"temps": "8h/semaine", "budget": "500€"},
        horizon_days=60,
    )
    upsert_context(payload, session)


def test_generate_options_is_capped_to_three() -> None:
    payload = {
        "primary_goal": "Changer de carrière",
        "success_definition": "Obtenir une offre",
        "constraints": {"temps": "10h"},
        "horizon_days": 30,
    }

    constraint_check = check_constraints(payload)
    options = generate_options(payload)

    assert constraint_check["ok"] is True
    assert len(options["options"]) <= 3


def test_decision_options_requires_existing_context(session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        decision_options(session)

    assert exc_info.value.status_code == 404


def test_decision_options_returns_structured_json(session: Session) -> None:
    _seed_context(session)

    response = decision_options(session)

    assert response.constraint_check.ok is True
    assert isinstance(response.options, list)
    assert 0 < len(response.options) <= 3
    assert all(option.title for option in response.options)


def test_decision_choose_rejects_missing_justification(session: Session) -> None:
    _seed_context(session)

    request = DecisionChooseRequest(
        options=["A", "B", "C"],
        chosen_option="A",
        abandoned_options=["B", "C"],
        justification="   ",
    )

    with pytest.raises(HTTPException) as exc_info:
        decision_choose(request, session)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Impossible de choisir sans justification."


def test_decision_choose_stores_decision(session: Session) -> None:
    _seed_context(session)

    request = DecisionChooseRequest(
        options=["Option 1", "Option 2", "Option 3"],
        chosen_option="Option 2",
        abandoned_options=["Option 1", "Option 3"],
        justification="Meilleur ratio impact/effort.",
    )

    response = decision_choose(request, session)

    assert response.validated is True
    assert response.chosen_option == "Option 2"
    assert response.abandoned_options == ["Option 1", "Option 3"]

    persisted = session.exec(select(Decision)).one()
    assert persisted.chosen_option == "Option 2"
    assert persisted.justification == "Meilleur ratio impact/effort."


def test_force_tradeoff_needs_abandoned_options() -> None:
    with pytest.raises(ValueError) as exc_info:
        force_tradeoff(chosen="A", justification="Parce que", abandoned=[])

    assert "option abandonnée" in str(exc_info.value)
