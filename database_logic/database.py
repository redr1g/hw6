from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
INTERNAL_KEY = "21bbd578633884affba9db6106ca3ecb"

db: Dict[str, str] = {}

class QARequest(BaseModel):
    question: str
    answer: str

vectorizer = TfidfVectorizer()

def check_internal_auth(token: str = Header(None)):
    """ Authenticate internal requests """
    if token != f"Bearer {INTERNAL_KEY}":
        raise HTTPException(status_code=403, detail="Unauthorized access to DB.")
    return {"message": "Internal request authenticated"}

# !!! client should have no access to this endpoint
@app.post("/write")
async def write_data(request: QARequest, authorization: str = Header(None)):
    """ Write data to the database """
    check_internal_auth(authorization)
    db[request.question] = request.answer
    return {"message": "Data written successfully!", "total": len(db)}

@app.get("/read")
async def read_data():
    return {"data": db}

@app.get("/read/{question}")
async def read_data(question: str,  authorization: str = Header(None)):
    """ Retrieve the answer to a specific question """
    
    check_internal_auth(authorization)
    if not db:
        return {"message": "No questions in the database."}
    
    # Check if the question is fully in database (optional)
    if question in db:
        return {"source": "cache", "question": question, "answer": db[question]}

    try:
        stored_questions = list(db.keys())
        all_questions = stored_questions + [question]
        tfidf_matrix = vectorizer.fit_transform(all_questions)
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        most_similar_idx = similarity_scores.argmax()
        
        if similarity_scores[0][most_similar_idx] > 0.9:
            most_similar_question = stored_questions[most_similar_idx]
            return {"source": "cache", "question": most_similar_question, "answer": db[most_similar_question]}
        else:
            raise HTTPException(status_code=204, detail="Successful request, but no semantically similar question found.")
    except ValueError as e:
            raise HTTPException(status_code=404, detail=f"Could not process request due to NLP: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Database service!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

