FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ai.py .
COPY runbooks ./runbooks

EXPOSE 8080

CMD ["python", "ai.py"]