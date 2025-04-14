import datetime
import os
import requests
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
import random

CLIENT_SERVICE_URL = "http://client_service:8002/ask"
VALID_TOKEN = "secret_token"

QUESTIONS = [
    "Що таке FastAPI?",
    "Розкажи про Python.",
    "Як працює machine learning?",
    "Що таке REST API?",
    "Які переваги Docker?",
    "Що таке Kubernetes?",
    "Як працює асинхронність у Python?",
    "Що таке мікросервіси?",
    "Що таке HTTP статус 404?",
    "Розкажи про SQL vs NoSQL"
    #add more if needed
]


def ping_client_logic():
    question = random.choice(QUESTIONS)
    payload = {"input_text": question}
    headers = {
        "Authorization": f"Bearer {VALID_TOKEN}"
    }
    try:
        # response = requests.get(BUSINESS_LOGIC_URL)
        # print(f"[Scheduler] Pinged business logic. Status: {response.status_code}, Response: {response.json()}")
        response = requests.post(CLIENT_SERVICE_URL, json=payload, headers=headers)
        print(f"[Scheduler] Sent {question}")
        response_data = response.json()
        cleaned_response = {key: value.strip() if isinstance(value, str) else value for key, value in response_data.items()}
        print(f"[Scheduler] Status {response.status_code}, Response: {cleaned_response}")
    except Exception as e:
        print(f"[Scheduler] Error pinging business logic: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(ping_client_logic, "interval", seconds=30, max_instances = 2) # is 30, bcuz it takes ~30 sec. to answer a question
                                                                # you can switch the endkey to /health and run it every 10 if desired :)
    scheduler.start()
    print("[Scheduler] Started.")
    yield
    scheduler.shutdown()
    print("[Scheduler] Shutdown.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Scheduler is running"}

if __name__ == "__main__":
    uvicorn.run("scheduler:app", host="0.0.0.0", port=8003, reload=True)