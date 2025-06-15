FROM python:3.9-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLASK_APP=app:app
ENV PYTHONPATH=/app

CMD ["python", "app.py"]