FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install openai python-dotenv fastapi uvicorn pydantic requests

EXPOSE 8000

CMD ["uvicorn", "business_logic:app", "--host", "0.0.0.0", "--port", "8000"]
