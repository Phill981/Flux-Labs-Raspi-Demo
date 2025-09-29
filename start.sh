#!/bin/bash

# Production startup script for Patient Vitals API

echo "Starting Patient Vitals API..."

# Check if patients_data.json exists
if [ ! -f "patients_data.json" ]; then
    echo "ERROR: patients_data.json not found!"
    echo "Please ensure the data file is present in the container."
    exit 1
fi

# Check file size
FILE_SIZE=$(stat -c%s "patients_data.json" 2>/dev/null || echo "0")
echo "Data file size: $((FILE_SIZE / 1024 / 1024)) MB"

# Start the application
echo "Starting FastAPI server..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --access-log \
    --log-level info
