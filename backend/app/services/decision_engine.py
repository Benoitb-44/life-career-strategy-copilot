from __future__ import annotations

from typing import Any


MAX_OPTIONS = 3


def check_constraints(context: dict[str, Any]) -> dict[str, Any]:
    primary_goal = str(context.get("primary_goal", "")).strip()
    success_definition = str(context.get("success_definition", "")).strip()
    constraints = context.get("constraints")
    horizon_days = context.get("horizon_days")

    if not primary_goal:
        return {
            "ok": False,
            "issue": "Le champ `primary_goal` est requis.",
            "suggested_adjustment": "Renseigner un objectif principal clair.",
        }

    if not success_definition:
        return {
            "ok": False,
            "issue": "Le champ `success_definition` est requis.",
            "suggested_adjustment": "Définir un critère de succès mesurable.",
        }

    if not isinstance(constraints, dict) or not constraints:
        return {
            "ok": False,
            "issue": "Le champ `constraints` doit contenir au moins une contrainte.",
            "suggested_adjustment": "Ajouter une contrainte (temps, budget, énergie, etc.).",
        }

    if horizon_days is not None and horizon_days > 90:
        return {
            "ok": False,
            "issue": "`horizon_days` ne peut pas dépasser 90.",
            "suggested_adjustment": "Réduire l'horizon ou diviser l'objectif en phases.",
        }

    return {"ok": True, "issue": ""}


def generate_options(context: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    primary_goal = str(context.get("primary_goal", "objectif")).strip() or "objectif"

    options = [
        {
            "title": "Trajectoire prudente",
            "value": f"Consolider les bases sur 4 semaines pour avancer vers: {primary_goal}",
            "effort": "modéré",
            "risk": "faible",
        },
        {
            "title": "Trajectoire équilibrée",
            "value": f"Lancer un plan d'exécution hebdomadaire orienté résultats pour: {primary_goal}",
            "effort": "élevé",
            "risk": "moyen",
        },
        {
            "title": "Trajectoire offensive",
            "value": f"Accélérer avec des paris à fort impact pour: {primary_goal}",
            "effort": "très élevé",
            "risk": "élevé",
        },
    ]

    return {"options": options[:MAX_OPTIONS]}


def force_tradeoff(chosen: str, justification: str, abandoned: list[str]) -> dict[str, Any]:
    if not chosen.strip():
        raise ValueError("Le choix doit être renseigné.")

    if not justification.strip():
        raise ValueError("Impossible de choisir sans justification.")

    if not abandoned:
        raise ValueError("L'arbitrage forcé exige au moins une option abandonnée.")

    if chosen in abandoned:
        raise ValueError("L'option choisie ne peut pas faire partie des options abandonnées.")

    return {
        "validated": True,
        "chosen_option": chosen,
        "justification": justification.strip(),
        "abandoned_options": abandoned,
    }
