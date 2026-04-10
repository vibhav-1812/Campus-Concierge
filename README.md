# HokieAssist — VT AI voice assistant

An AI-assisted voice assistant for Virginia Tech students: dining status, Blacksburg Transit, club events, and natural-language campus questions.

## Features

- **Voice interaction**: Speech-to-text and text-to-speech (Web Speech API)
- **Backend routing**: FastAPI with NLU for transit intents and keyword routing to live data scrapers
- **OpenAI (optional)**: Used in `backend/nlu.py` when configured for parsing fallbacks (see `env.example`)
- **Real-time data**: Scraping / HTTP access to UDC dining, Blacksburg Transit, and Gobbler Connect
- **Frontend**: React 18, TypeScript, TailwindCSS, Vite

## Architecture

### Backend (FastAPI)

- **FastAPI**: REST API with CORS for the React dev server
- **`nlu.py`**: Regex/heuristic parsing for transit intents (`transit_route`, `next_bus`) and campus place normalization
- **`langchain_agent.py`**: Legacy filename; routes general queries to scrapers by keywords (no LangChain in current code path)
- **`scrapers/`**: Dining, bus, and club event data access
- **Google Maps / NVIDIA NIM**: Optional keys in `.env` for enhanced transit features (see `backend/main.py` root response)

### Frontend (React + TypeScript)

- **Vite** dev server (default port is often **5173**, not 3000)
- **Axios** client to `POST /ask` on `http://localhost:8000`

## Quick start

### Prerequisites

- Python 3.10+ recommended (uses `str | None` style types)
- Node.js 18+
- API keys as needed: see `backend/env.example`

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env
# Edit .env with your keys
python main.py
```

API: `http://localhost:8000` — interactive docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints in the terminal (typically `http://localhost:5173`).

## API endpoints (summary)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/ask` | Main chat query; transit vs scraper routing |
| POST | `/bus/query` | Dedicated bus/transit query with optional origin |
| GET | `/dining` | Dining hall status |
| GET | `/bus` | Bus times snapshot |
| GET | `/clubs` | Club events |

## Development

```bash
# Backend with reload
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm run build
```

## PM4 documentation

- **`IMPLEMENTATION.md`** — Milestone implementation summary and AI disclosure (course requirement)
- **`docs/AI_USAGE_LOG.md`** — Concise log of which areas used generative-AI tooling

## Troubleshooting

- **Voice**: Use Chrome or Edge; grant microphone permission.
- **API errors**: Confirm backend on port 8000 and `.env` keys if using Maps / OpenAI.
- **Scraping**: External sites may change HTML or rate-limit; behavior can degrade without notice.

## License

MIT (see `LICENSE` if present in your fork).

Built for Virginia Tech students.
