import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine

pytest.importorskip("reportlab")

from app.api.plan import export_plan_pdf
from app.models import ChecklistResult, Plan90Days, PlanStatus


def _create_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_export_pdf_returns_403_when_plan_not_approved() -> None:
    with _create_session() as session:
        plan = Plan90Days(
            user_id=1,
            status=PlanStatus.draft,
            plan_json={
                "objective": "Test objective",
                "monthly_objectives": [],
                "kpis": [],
                "risks": [],
            },
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)

        with pytest.raises(HTTPException) as exc_info:
            export_plan_pdf(plan.id or 0, session)

        assert exc_info.value.status_code == 403


def test_export_pdf_returns_pdf_when_plan_approved() -> None:
    with _create_session() as session:
        plan = Plan90Days(
            user_id=1,
            status=PlanStatus.approved,
            plan_json={
                "objective": "Land 3 interviews",
                "monthly_objectives": [
                    {"month": 1, "objective": "Positioning", "deliverables": ["CV update"]},
                    {"month": 2, "objective": "Outreach", "deliverables": ["20 applications"]},
                    {"month": 3, "objective": "Interviewing", "deliverables": ["Mock interviews"]},
                ],
                "kpis": ["3 interview loops"],
                "risks": ["Time constraints"],
            },
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)

        session.add(
            ChecklistResult(
                plan_id=plan.id or 0,
                clarity=True,
                focus=True,
                actionability=True,
                feasibility=True,
                risk_awareness=True,
                coherence=True,
                verdict="approved",
                feedback="Good plan.",
            )
        )
        session.commit()

        response = export_plan_pdf(plan.id or 0, session)

        assert response.status_code == 200
        assert response.media_type == "application/pdf"
        assert response.body.startswith(b"%PDF")
