#!/usr/bin/env bash
# Wait for the database to be available, then start Uvicorn
set -e

python - <<'PY'
import os
import time
import sys
import psycopg2

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/fastapi_db')
print('Waiting for database at', db_url)
for i in range(60):
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        print('Database is available')
        break
    except Exception as e:
        print('Database unavailable, retrying...', str(e))
        time.sleep(1)
else:
    print('Timed out waiting for the database', file=sys.stderr)
    sys.exit(1)
PY

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
