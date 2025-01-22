FROM python:3.11-slim

ARG SERVICE_NAME

WORKDIR /app

COPY shared /app/shared
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ${SERVICE_NAME} .

CMD ["python", "main.py"]
