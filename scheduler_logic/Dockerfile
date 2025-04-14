FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn[standard] apscheduler requests

EXPOSE 8003

CMD ["uvicorn", "scheduler:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
