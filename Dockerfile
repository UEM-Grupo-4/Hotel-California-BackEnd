FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "\
echo '⏳ Waiting for MySQL...' && \
while ! nc -z $DB_HOST $DB_PORT; do sleep 0.5; done && \
echo '✅ MySQL is up!' && \
cd backend_django && \
python manage.py makemigrations && \
python manage.py migrate && \
python manage.py seed_data && \
echo '🚀 Starting Daphne...' && \
exec daphne config.asgi:application -b 0.0.0.0 -p 8000 \
"]
