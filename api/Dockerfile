FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN ls -l /app

EXPOSE 80

# Démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]