FROM python:3.9-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLASK_APP=app:app
ENV PYTHONPATH=/app

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]