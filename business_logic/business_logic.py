import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI()

class TextRequest(BaseModel):
    input_text: str

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
INTERNAL_KEY = "499ac1ef4f22ce1333e2a10ac04fd53d"

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OpenRouter API Key. Set OPENROUTER_API_KEY in the .env file.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def check_internal_auth(token: str = Header(None)):
    """ Authenticate internal requests """
    if token != f"Bearer {INTERNAL_KEY}":
        raise HTTPException(status_code=403, detail="Unauthorized access to Business Logic.")
    return {"message": "Internal request authenticated"}

# !!! client should have no access to this endpoint
@app.post("/process")
async def process_text(request: TextRequest, authorization: str = Header(None)):
    """ Calls OpenRouter via OpenAI client for text processing """
    check_internal_auth(authorization)
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[{"role": "user", "content": request.input_text}],
            extra_body={}
        )

        response = completion.choices[0].message.content
        return response

    except Exception as e:
        return HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Business Logic service!"}
