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
echo "Применение миграций БД..."
python manage.py makemigrations
python manage.py migrate
echo "Миграция БД завершена."
echo "Сбор статики Django..."
python manage.py collectstatic
echo "Статика Django собрана."
# Запуск основной команды контейнера (переданной через CMD)
exec "$@"