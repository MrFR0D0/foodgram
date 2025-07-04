FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0:8000", "foodgram_backend.wsgi:application"]
