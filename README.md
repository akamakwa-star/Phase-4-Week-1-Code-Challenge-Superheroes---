# Superheroes API

Simple Flask API for tracking heroes and their powers — Phase 4 Week 1 Code Challenge.

Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Seed the database:

```bash
python seed.py
```

3. Run the app:

```bash
python app.py
```

Routes

- `GET /heroes` — list heroes
- `GET /heroes/<id>` — show hero with nested `hero_powers`
- `GET /powers` — list powers
- `GET /powers/<id>` — show a power
- `PATCH /powers/<id>` — update a power's description
- `POST /hero_powers` — create a new hero_power relation

Notes

- Model validations are enforced via SQLAlchemy `@validates` decorators. Errors are returned as JSON.
