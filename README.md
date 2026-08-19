# flask-ai-agent — AI-Company Delivery Template

A production-ready Flask backend for **LLM-backed conversational services**: FAQ
chatbots, email auto-responders / triage, support-ticket classifiers, and
retrieval-augmented assistants. Maps directly to catalog items #1, #10, #15, #20.

## What you get
- `app.py` — Flask API with `/health`, `/chat` (single-turn), `/chat/multi`
  (multi-turn memory), and `/classify` (label + route). Includes a flag-gated
  rule-based fallback so it runs with **no API key**.
- `ai_client.py` — shared AI scaffolding (OpenAI-compatible, stdlib-only,
  feature-flagged). See `shared/ai_client.py` for the contract.
- `.github/workflows/ci.yml` — lint + test + build on push/PR.
- `tests/test_app.py` — offline tests (AI disabled).
- `requirements.txt` — pinned deps.

## Quick start
```bash
pip install -r requirements.txt
export AI_ENABLED=true            # false = offline rule-based mode
export AI_API_KEY=sk-...          # optional; falls back to rules if empty
export AI_BASE_URL=https://api.openai.com/v1
export AI_MODEL=gpt-4o-mini
python app.py
curl localhost:5000/health
```

## Endpoints
| Method | Path           | Purpose                                  |
|--------|----------------|------------------------------------------|
| GET    | `/health`      | Liveness / readiness                     |
| POST   | `/chat`        | `{ "message": "..." }` -> `{ "reply": "..." }` |
| POST   | `/chat/multi`  | `{ "messages": [...] }` -> `{ "reply": "..." }` |
| POST   | `/classify`    | `{ "text": "...", "labels": [...] }` -> `{ "label": "...", "reason": "..." }` |

## Feature flags (env)
All optional. `AI_ENABLED=false` makes the app fully functional offline with
deterministic rule-based responses (great for demos + CI).

## Deploy
- Local: `gunicorn -w 4 app:app`
- Container: `Dockerfile` exposes port 5000.
