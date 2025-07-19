FROM python:3.12-alpine

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0:8000", "src.foodgram.wsgi:application"]
