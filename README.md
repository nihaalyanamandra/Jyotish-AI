# Jyotish AI — Full-stack MVP

A runnable Vedic astrology studio with a Next.js frontend and FastAPI backend. It computes sidereal Lahiri D1, D9, D10, whole-sign houses, planetary nakshatras and Vimshottari Mahadasha/Antardasha timelines. Chat is grounded in the computed chart and uses the OpenAI API when configured.

## Architecture

```text
Browser / Next.js 15 (port 3000)
  ├── Birth input, D1/D9/D10 explorer, dasha timeline, chat
  └── REST JSON
        └── FastAPI (port 8000)
              ├── POST /chart → Swiss Ephemeris (Moshier) + Lahiri + Vimshottari
              ├── GET /transits → current sidereal planetary positions
              └── POST /chat → computed chart + OpenAI API (server-side key)
```

## Run locally

Requirements: Python 3.11+ and Node.js 20+.

**Terminal 1 — backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export OPENAI_API_KEY='your-key'  # optional; without it chat uses an offline explanation
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. API docs: http://localhost:8000/docs.

## Validation

```bash
cd backend
pytest -q
```

## MVP limitations and production roadmap

- The UI starts with **sample birth details** (Nagpur, India); replace them before generating a personal chart. Coordinates and IANA time zone must be provided manually; add a geocoding/time-zone lookup in production.
- Swiss Ephemeris uses the **Moshier** built-in ephemeris, **mean lunar node**, and **Lahiri ayanamsa**. Divisional charts use sign mappings (D9/D10), not separate divisional ascendant astronomical recalculations. Dasha dates use 365.2425-day solar-year convention; other schools/software may differ. No Pratyantardasha or event prediction engine is included.
- Whole-sign houses are used; other Jyotish house systems can give different bhava placements. DST/time zone depends on the installed IANA database.
- OpenAI calls run only on the server. No account system or database: birth details and chat history remain in browser memory and are lost on refresh. Add authenticated profiles, encrypted storage, consent, export/delete, rate limits, observability and abuse controls before production.
- The chat API sends the chart and recent user messages to the configured AI provider; disclose this clearly before production use. Keep API keys on the server.
- Astrology is a cultural interpretive practice, not scientifically established for predicting personal outcomes. The agent must distinguish chart facts from interpretations and avoid guarantees.
- Swiss Ephemeris licensing requires review before commercial deployment; confirm whether your intended use needs a commercial license or AGPL compliance.
