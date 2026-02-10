from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChecklistEvaluation:
    clarity: bool
    focus: bool
    actionability: bool
    feasibility: bool
    risk_awareness: bool
    coherence: bool
    verdict: str
    feedback: str


def _words_count(value: Any) -> int:
    if not isinstance(value, str):
        return 0
    return len([word for word in value.split() if word.strip()])


def evaluate_plan_checklist(plan: dict[str, Any]) -> ChecklistEvaluation:
    objective = plan.get("objective") if isinstance(plan, dict) else None
    monthly_objectives = plan.get("monthly_objectives") if isinstance(plan, dict) else None
    kpis = plan.get("kpis") if isinstance(plan, dict) else None
    risks = plan.get("risks") if isinstance(plan, dict) else None

    has_valid_months = isinstance(monthly_objectives, list) and len(monthly_objectives) == 3
    has_valid_kpis = isinstance(kpis, list) and len(kpis) >= 2

    clarity = isinstance(objective, str) and _words_count(objective) >= 6

    focus = (
        has_valid_months
        and sum(1 for month in monthly_objectives if isinstance(month, dict)) == 3
        and all(
            isinstance(month.get("objective"), str) and _words_count(month.get("objective")) >= 3
            for month in monthly_objectives
        )
    )

    actionability = has_valid_months and all(
        isinstance(month.get("deliverables"), list)
        and len(month.get("deliverables")) >= 1
        and all(isinstance(deliverable, str) and _words_count(deliverable) >= 2 for deliverable in month.get("deliverables"))
        for month in monthly_objectives
        if isinstance(month, dict)
    )

    feasibility = has_valid_months and all(
        isinstance(month.get("deliverables"), list) and len(month.get("deliverables")) <= 5
        for month in monthly_objectives
        if isinstance(month, dict)
    )

    risk_awareness = isinstance(risks, list) and len(risks) >= 1 and all(
        isinstance(risk, str) and _words_count(risk) >= 3 for risk in risks
    )

    coherence = (
        has_valid_months
        and has_valid_kpis
        and clarity
        and isinstance(kpis, list)
        and all(isinstance(kpi, str) and _words_count(kpi) >= 2 for kpi in kpis)
    )

    criteria = {
        "clarity": clarity,
        "focus": focus,
        "actionability": actionability,
        "feasibility": feasibility,
        "risk_awareness": risk_awareness,
        "coherence": coherence,
    }

    failed = [name for name, is_valid in criteria.items() if not is_valid]
    verdict = "rejected" if failed else "approved"

    if not failed:
        feedback = "Plan validé : checklist complète et cohérente."
    else:
        feedback = (
            "Plan rejeté : corriger "
            + ", ".join(failed)
            + ". Recommandé : préciser l'objectif, détailler des livrables actionnables, ajouter KPI et risques explicites."
        )

    return ChecklistEvaluation(
        clarity=clarity,
        focus=focus,
        actionability=actionability,
        feasibility=feasibility,
        risk_awareness=risk_awareness,
        coherence=coherence,
        verdict=verdict,
        feedback=feedback,
    )
