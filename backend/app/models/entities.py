from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PlanStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    rejected = "rejected"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class CareerContext(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    primary_goal: str
    success_definition: str
    constraints: dict = Field(sa_column=Column(JSON, nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)


class Decision(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    options: list[str] = Field(sa_column=Column(JSON, nullable=False))
    chosen_option: str
    abandoned_options: list[str] = Field(sa_column=Column(JSON, nullable=False))
    justification: str
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class Plan90Days(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    plan_json: dict = Field(sa_column=Column(JSON, nullable=False))
    status: PlanStatus = Field(default=PlanStatus.draft, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class ChecklistResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="plan90days.id", index=True)
    goals_clear: bool = Field(default=False, nullable=False)
    measurable_milestones: bool = Field(default=False, nullable=False)
    realistic_scope: bool = Field(default=False, nullable=False)
    has_risks_and_mitigations: bool = Field(default=False, nullable=False)
    verdict: str
    feedback: str
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
