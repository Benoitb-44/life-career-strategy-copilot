from __future__ import annotations

from hashlib import sha256
from typing import Any

MIN_BETS = 2
MAX_BETS = 3


def _normalize_text(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text or default


def _stable_index(seed: str, modulo: int) -> int:
    digest = sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % modulo


def generate_strategic_bets(context: dict[str, Any], chosen_option: str) -> list[dict[str, str]]:
    """Generate deterministic mock strategic bets.

    Output is always a non-empty list that conforms to the expected schema:
    hypothesis, success_signal, main_risk, fallback.
    """

    goal = _normalize_text(context.get("primary_goal"), "votre objectif prioritaire")
    success_definition = _normalize_text(context.get("success_definition"), "un signal de progression mesurable")
    option = _normalize_text(chosen_option, "option prioritaire")

    templates = [
        {
            "hypothesis": f"En exécutant '{option}' de manière focus 2 semaines, nous accélérons vers {goal}.",
            "success_signal": f"Un livrable concret est produit et valide {success_definition}.",
            "main_risk": "Dispersion opérationnelle qui ralentit l'exécution.",
            "fallback": "Réduire le périmètre à une seule action critique et replanifier sur 7 jours.",
        },
        {
            "hypothesis": f"Une routine hebdomadaire orientée résultats rend '{option}' soutenable pour atteindre {goal}.",
            "success_signal": "Deux itérations complètes sont terminées sans rupture de rythme.",
            "main_risk": "Charge personnelle imprévue qui casse la cadence.",
            "fallback": "Passer en mode minimum viable (30 minutes/jour) jusqu'au retour à la normale.",
        },
        {
            "hypothesis": f"En obtenant du feedback externe tôt, '{option}' augmente ses chances de succès sur {goal}.",
            "success_signal": "Au moins un retour externe actionnable est intégré au plan.",
            "main_risk": "Feedback tardif ou non exploitable.",
            "fallback": "Utiliser une auto-revue structurée avec checklist en attendant un retour externe.",
        },
    ]

    selected_size = MIN_BETS + _stable_index(f"{goal}|{option}", MAX_BETS - MIN_BETS + 1)
    offset = _stable_index(f"{option}|{success_definition}", len(templates))

    rotated = templates[offset:] + templates[:offset]
    bets = rotated[:selected_size]

    return bets or [templates[0]]
