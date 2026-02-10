# Backend FastAPI

Ce dossier contient le backend FastAPI minimal pour le projet.

## Prérequis

- Python 3.10+

## Installation

Depuis le dossier `backend/` :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

> Alternative : `pip install -e .` (via `pyproject.toml`).

## Variables d'environnement

Copier le fichier d'exemple :

```bash
cp .env.example .env
```

Puis compléter les valeurs nécessaires.

- `DATABASE_URL` est optionnelle ; par défaut, SQLite est utilisé : `sqlite:///./copilot.db`.
- `LLM_MOCK` (optionnelle) : `true` pour activer un mode mock stable qui ne nécessite pas de clé OpenAI.
- `OPENAI_API_KEY` est requise uniquement si `LLM_MOCK` est désactivé.
- `LLM_TIMEOUT_S`, `LLM_RETRIES`, `LLM_MODEL` permettent d’ajuster le client LLM.


## Initialiser la base de données

Depuis `backend/` :

```bash
python scripts/init_db.py
```

## Lancer le serveur

Depuis `backend/` :

```bash
uvicorn app.main:app --reload
```

Au démarrage, les tables SQLModel sont créées automatiquement si elles n'existent pas.

Application disponible sur : `http://127.0.0.1:8000`

## Vérification santé

```bash
curl http://127.0.0.1:8000/health
```

Réponse attendue :

```json
{"status":"ok"}
```

## Prompts versionnés

Les prompts sont stockés dans `app/prompts/` (ex: `system_prompt.md`) et chargés par `app/services/llm_client.py` via `run_prompt(prompt_name, input_json)`.
