# 1. Wähle ein offizielles Python-Basisimage
FROM python:3.11-slim

# 2. Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# 3. Kopiere zuerst nur die requirements.txt-Datei
#    Docker nutzt Caching: Dieser Schritt wird nur wiederholt, wenn sich die Datei ändert
COPY requirements.txt .

# 4. Installiere die Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kopiere den Rest des Anwendungscodes (main.py und data.json)
COPY . .

# 6. Informiere Docker, dass der Container auf Port 8000 lauscht
EXPOSE 8009

# 7. Definiere den Befehl, der beim Starten des Containers ausgeführt wird
#    --host 0.0.0.0 ist wichtig, damit der Server von außerhalb des Containers erreichbar ist
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8009"]
