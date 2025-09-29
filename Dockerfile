# 1. Use an official Python base image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy only requirements first (for caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the app
COPY . .

# 6. Expose port (8009 in your CMD)
EXPOSE 8009

# 7. Add healthcheck (adjust /health endpoint to your app)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8009/health || exit 1

# 8. Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]