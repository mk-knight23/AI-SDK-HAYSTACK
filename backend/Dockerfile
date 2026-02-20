# Backend Dockerfile - Django
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "trendfactory.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
