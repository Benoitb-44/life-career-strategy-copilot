from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine

from app.api.context import CareerContextUpsertRequest, get_context, upsert_context


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session


def test_upsert_and_get_context_ok(session: Session) -> None:
    payload = CareerContextUpsertRequest(
        primary_goal="Reconversion vers data",
        success_definition="Avoir une offre signée",
        constraints={"temps": "10h/semaine"},
        horizon_days=60,
    )

    created = upsert_context(payload, session)

    assert created.primary_goal == payload.primary_goal
    assert created.success_definition == payload.success_definition
    assert created.constraints == payload.constraints
    assert created.horizon_days == payload.horizon_days
    assert isinstance(created.updated_at, datetime)

    fetched = get_context(session)
    assert fetched.user_id == created.user_id
    assert fetched.primary_goal == payload.primary_goal


def test_upsert_context_invalid_payload_returns_400(session: Session) -> None:
    payload = CareerContextUpsertRequest(
        primary_goal="   ",
        success_definition="",
        constraints={},
        horizon_days=120,
    )

    with pytest.raises(HTTPException) as exc_info:
        upsert_context(payload, session)

    assert exc_info.value.status_code == 400
    errors = exc_info.value.detail
    assert "`primary_goal` doit être renseigné." in errors
    assert "`success_definition` doit être renseigné." in errors
    assert "`constraints` doit contenir au moins une contrainte." in errors
    assert "`horizon_days` doit être inférieur ou égal à 90." in errors


def test_get_context_not_found(session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_context(session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "CareerContext introuvable."
