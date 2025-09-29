FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8009

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=1 \
    CMD curl -f http://localhost:8009/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]
