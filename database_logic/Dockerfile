FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install fastapi uvicorn pydantic typing scikit-learn scipy

EXPOSE 8001

CMD ["uvicorn", "database:app", "--host", "0.0.0.0", "--port", "8001"]
