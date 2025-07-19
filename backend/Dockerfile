# --- Этап 1: Установка зависимостей (Builder) ---
FROM python:3.12-alpine AS builder

WORKDIR /app

RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r /app/requirements.txt --no-cache-dir
COPY . .

RUN chmod +x /app/entrypoint.sh

 # --- Этап 2: Создание финального, чистого образа ---
FROM python:3.12-alpine

WORKDIR /app

# Копируем установленные пакеты из builder-образа
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Копируем исполняемые файлы (gunicorn, etc.)
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем код приложения из builder-образа
COPY --from=builder /app /app

ENTRYPOINT ["/app/entrypoint.sh"] 

CMD ["gunicorn", "--bind", "0:8000", "src.foodgram.wsgi:application"]