FROM python:3.12-slim

# psycopg2's fix
RUN apt-get update && apt-get -y install libpq-dev gcc

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "url_shortener.api:app", "--host", "0.0.0.0", "--port", "8000"]
