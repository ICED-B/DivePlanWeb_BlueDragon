#!/bin/bash

echo "=== DivePlanWeb Backend Startup ==="

# Run DB migrations with retry (max 5x, 90s hard timeout per attempt)
# Import Flask app + DB connect + schema creation takes ~20-30s on cold start
# case 5x95s=475s < 600s Azure limit
echo "Running DB migrations..."
MIGRATED=0
for i in $(seq 1 5); do
    if timeout 90 flask db upgrade; then
        echo "Migrations OK on attempt $i"
        MIGRATED=1
        break
    fi
    echo "Attempt $i/5 failed. Retrying in 5s..."
    sleep 5
done

if [ "$MIGRATED" = "0" ]; then
    echo "WARNING: All migration attempts failed. Starting gunicorn anyway."
fi

echo "Starting gunicorn on 0.0.0.0:8000 ..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    run:app
