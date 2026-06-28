FROM python:3.11-slim

WORKDIR /app

COPY services/shared /app/shared
COPY services/signal-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/signal-processor/main.py .

ENV PYTHONPATH=/app/shared
ENV PYTHONUNBUFFERED=1

EXPOSE 8001 8080

CMD ["python", "main.py"]
