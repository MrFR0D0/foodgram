#!/bin/sh

# Ожидание готовности базы данных (опционально, но очень рекомендуется)
# 'db' - это имя сервиса базы данных в вашем docker-compose.yml
# Если у вас другое имя сервиса БД, замените 'db' на него.
# Порт 5432 - стандартный для PostgreSQL.
# echo "Waiting for database..."
# while ! nc -z db 5432; do
#   sleep 0.1
# done
# echo "Database started."

# Применение миграций Django
echo "\nПрименение миграций БД...\n"
python manage.py makemigrations
python manage.py migrate
echo "\nМиграция БД завершена."

echo "\nСбор статики Django..."
python manage.py collectstatic
cp -r /app/collected_static/. /django_static/static
echo "Статика Django собрана."

echo "\nЗагрузка тегов и ингридиентов..."
python manage.py import_data

echo "\nЗагрузка пользователей..."
python manage.py import_users

echo "\nДобавление аватарок пользователей..."
python manage.py set_avatars

echo "\nСоздание рецептов..."
python manage.py create_recipes
# Запуск основной команды контейнера (переданной через CMD)
exec "$@"