FROM python:3.12

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip &&     pip install --default-timeout=300 -r /app/requirements.txt --no-cache-dir

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0:8000", "src.foodgram.wsgi:application"]
