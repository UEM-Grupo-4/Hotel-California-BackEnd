#!/bin/bash
# entrypoint.sh

# Espera a que MySQL esté listo
echo "⏳ Waiting for MySQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
ls
cd hotel_backend
echo "✅ MySQL is up!"

# Migraciones
echo "🛠 Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Seeds
# echo "🌱 Running seed_all..."
# python manage.py seed_all

# Arranca el server
echo "🚀 Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000