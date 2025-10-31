## Guarded Chat Service (Guardrails.ai)

A minimal FastAPI service that detects unsafe prompts and filters model outputs using Guardrails.ai before proxying to an LLM.

### Features
- Input guard: blocks unsafe prompts (toxicity, PII, prompt injection heuristics)
- Output guard: filters/sanitizes unsafe generations
- Simple `/chat` endpoint with lamma (swap to any LLM)

### Requirements
- Python 3.10+
- Environment variables (create a `.env` file in project root):
  - `GROQ_API_KEY` (required for Groq backend)
  - Optional keys depending on validators you enable in the RAIL (e.g., `PERSPECTIVE_API_KEY`)

### Setup
```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell: . .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

### Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run the Streamlit UI (optional):
```bash
streamlit run streamlit_app.py
```

### Use
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me a joke about cats"}'
```

### Customize Safety Rules
Edit the RAIL file at `rails/safety.rail` to add/remove validators or tune thresholds. Some validators may require additional API keys.

### Notes
- The provided RAIL uses common validators where available. If a validator requires an external API (e.g., Perspective) and no key is set, it will be skipped or fall back to conservative handling.
- The backend now uses Groq's OpenAI-compatible API with `llama-3.1-8b-instant`. Set `GROQ_API_KEY` in `.env`.


