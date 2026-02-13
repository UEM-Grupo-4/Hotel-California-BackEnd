FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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
echo DB_HOST=$DB_HOST && \
echo DB_PORT=$DB_PORT && \
echo '⏳ Waiting for MySQL...' && \
while ! nc -z $DB_HOST $DB_PORT; do sleep 0.5; done && \
echo '✅ MySQL is up!' && \
cd hotel_backend && \
echo '🛠 Running migrations...' && \
python manage.py makemigrations && \
python manage.py migrate && \
echo '🚀 Starting Django server...' && \
exec python manage.py runserver 0.0.0.0:8000 \
"]
