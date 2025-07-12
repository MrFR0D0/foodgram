#!/bin/sh

echo "\nПрименение миграций БД...\n"
python manage.py makemigrations
python manage.py migrate
echo "\nМиграция БД завершена."

echo "\nСбор статики Django..."
python manage.py collectstatic
cp -r /app/src/collected_static/. /django_static/static
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