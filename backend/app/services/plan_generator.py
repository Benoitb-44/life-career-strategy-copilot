from __future__ import annotations

from hashlib import sha256
from typing import Any

FORBIDDEN_DELIVERABLE_TERMS = (
    "learn",
    "explore",
    "get familiar",
    "apprendre",
    "explorer",
    "se familiariser",
    "se familiarise",
    "prise en main",
)


def _normalize_text(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text or default


def _stable_index(seed: str, modulo: int) -> int:
    digest = sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % modulo


def _contains_forbidden_terms(text: str) -> bool:
    normalized = text.casefold()
    return any(term in normalized for term in FORBIDDEN_DELIVERABLE_TERMS)


def _validate_deliverables(deliverables: list[str]) -> None:
    for deliverable in deliverables:
        if _contains_forbidden_terms(deliverable):
            raise ValueError(
                "Deliverables cannot include learning/exploration phrasing "
                f"('{deliverable}')."
            )


def generate_plan_90_days(context: dict[str, Any], chosen_option: str) -> dict[str, Any]:
    """Generate a canonical 90-day plan JSON.

    Schema:
    - objective
    - monthly_objectives (exactly 3 months, each with deliverables)
    - kpis
    - risks
    """

    goal = _normalize_text(context.get("primary_goal"), "Atteindre un objectif professionnel prioritaire")
    success = _normalize_text(context.get("success_definition"), "un résultat mesurable")
    option = _normalize_text(chosen_option, "la trajectoire prioritaire")

    objective = f"Exécuter '{option}' pour progresser vers : {goal}."

    month_templates = [
        {
            "objective": f"Valider le cadrage opérationnel de '{option}' avec un périmètre réaliste.",
            "deliverables": [
                "Document de périmètre validé avec priorités, jalons et critères de décision.",
                "Backlog priorisé des actions des 4 prochaines semaines avec responsables et échéances.",
            ],
        },
        {
            "objective": f"Produire des résultats tangibles alignés sur {goal}.",
            "deliverables": [
                "Deux livrables métier publiables démontrant une progression concrète.",
                "Revue mi-parcours avec ajustements formalisés, impacts et nouvelles priorités.",
            ],
        },
        {
            "objective": f"Consolider la traction et démontrer {success}.",
            "deliverables": [
                "Dossier de preuves d'impact comprenant résultats, métriques et retours actionnables.",
                "Plan de continuation 90 jours avec séquencement des prochaines exécutions.",
            ],
        },
    ]

    offset = _stable_index(f"{goal}|{option}|{success}", len(month_templates))
    rotated = month_templates[offset:] + month_templates[:offset]

    monthly_objectives = [
        {
            "month": month_number,
            "objective": template["objective"],
            "deliverables": template["deliverables"],
        }
        for month_number, template in enumerate(rotated, start=1)
    ]

    for month in monthly_objectives:
        _validate_deliverables(month["deliverables"])

    kpis = [
        {
            "name": "Livrables critiques produits",
            "target": ">= 4 livrables validés sur 90 jours",
        },
        {
            "name": "Cadence hebdomadaire",
            "target": ">= 10 sessions d'exécution par mois",
        },
        {
            "name": "Signal de succès principal",
            "target": success,
        },
    ]

    risks = [
        {
            "risk": "Dispersion des efforts sur des actions à faible impact",
            "mitigation": "Limiter le WIP à 3 priorités et faire une revue hebdomadaire.",
        },
        {
            "risk": "Sous-estimation de la charge disponible",
            "mitigation": "Bloquer des créneaux fixes et réduire le périmètre en cas de dérive.",
        },
        {
            "risk": "Absence de feedback exploitable",
            "mitigation": "Planifier des points de revue récurrents et collecter des retours actionnables.",
        },
    ]

    return {
        "objective": objective,
        "monthly_objectives": monthly_objectives,
        "kpis": kpis,
        "risks": risks,
    }
