#!/bin/sh

set -u
# Run migrations
alembic upgrade head

python -m uvicorn --host=0.0.0.0 app.main:app --reload
