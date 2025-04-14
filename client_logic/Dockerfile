FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install fastapi uvicorn requests python-dotenv pydantic

EXPOSE 8002

CMD ["uvicorn", "client:app", "--host", "0.0.0.0", "--port", "8002"]