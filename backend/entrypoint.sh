#!/bin/sh
set -e
python -m alembic upgrade head || echo "alembic skipped"
python -m app.seed || true
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
