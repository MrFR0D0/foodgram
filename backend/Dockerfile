FROM python:3.12-alpine

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip && \
    pip install -r /app/requirements.txt --no-cache-dir

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0:8000", "src.foodgram.wsgi:application"]
