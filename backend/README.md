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

## Lancer le serveur

Depuis `backend/` :

```bash
uvicorn app.main:app --reload
```

Application disponible sur : `http://127.0.0.1:8000`

## Vérification santé

```bash
curl http://127.0.0.1:8000/health
```

Réponse attendue :

```json
{"status":"ok"}
```
