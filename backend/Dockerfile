FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SMART_HOME_DB=/app/data/smarthome.sqlite

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY db ./db

RUN mkdir -p /app/data
EXPOSE 3001

# Las migraciones y semillas se aplican al iniciar la API.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
