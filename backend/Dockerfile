FROM python:3.12

WORKDIR /app

# RUN apt-get update && apt-get install -y postgresql-client netcat-traditional

COPY requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

# CMD ["python", "manage.py", "runserver", "0:8000"]
CMD ["gunicorn", "--bind", "0:8000", "foodgram.wsgi:application"]
