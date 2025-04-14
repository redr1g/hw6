import os
import requests
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

DATABASE_SERVICE_URL = "http://database_logic:8001"
INTERNAL_DATABASE_KEY = "21bbd578633884affba9db6106ca3ecb"
BUSINESS_LOGIC_SERVICE_URL = "http://business_logic:8000"
INTERNAL_BUSINESS_KEY = "499ac1ef4f22ce1333e2a10ac04fd53d"

VALID_TOKEN = 'secret_token'

app = FastAPI()

class QuestionRequest(BaseModel):
    input_text: str

def check_auth(token: str = Header(None)):
    """ Simple token authentication """
    if token != f"Bearer {VALID_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return {"message": "You are authorized!"}

@app.post("/ask")
async def ask_question(request: QuestionRequest, authorization: str = Header(None)):
    """
    - Checks if the question exists in the Database Service.
    - If found, returns cached response.
    - Otherwise, calls Business Logic Service and saves the answer.
    """
    check_auth(authorization)

    # Check cache (Database Service)
    cache_response = requests.get(
        f"{DATABASE_SERVICE_URL}/read/{request.input_text}",
        headers = {"Authorization": f"Bearer {INTERNAL_DATABASE_KEY}"})
    if cache_response.status_code == 200:
        cached_data = cache_response.json()
        if cached_data.get("answer"):
            return {"source": "cache", "answer": cached_data["answer"]}

    # Call Business Logic Service for processing (question not found in cache)
    bl_response = requests.post(
        f"{BUSINESS_LOGIC_SERVICE_URL}/process", 
        json={"input_text": request.input_text},
        headers={"Authorization": f"Bearer {INTERNAL_BUSINESS_KEY}"}
    )
    if bl_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error processing question")

    answer = bl_response.json()

    requests.post(
        f"{DATABASE_SERVICE_URL}/write", 
        json={"question": request.input_text, "answer": answer}, 
        headers={"Authorization": f"Bearer {INTERNAL_DATABASE_KEY}"}
    )

    return {"source": "business_logic", "answer": answer}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/")
async def root():
    """ Service description """
    return {"message": "Client Service: Orchestrates requests between users, Business Logic, and Database Service"}
