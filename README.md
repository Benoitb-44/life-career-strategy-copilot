# Life / Career Strategy Copilot

An AI copilot designed to help senior professionals decide
what to do in the next 90 days — and why.

## Aha Moment
"I know exactly what to do for the next 3 months."

## What this product is NOT
- Not a career chatbot
- Not a coaching app
- Not a productivity tool

## Core Artifact
A decision-grade 90-day career strategy PDF.

## Why it matters
Bad career decisions are costly.
This product optimizes for clarity, not advice.

## Lancement en développement avec Docker Compose

Depuis la racine du dépôt :

```bash
docker compose up
```

Cette commande lance :

- `backend` : FastAPI avec `uvicorn` sur `http://localhost:8000`
- `frontend` : Next.js en mode dev sur `http://localhost:3000`

Arrêter les services :

```bash
docker compose down
```
