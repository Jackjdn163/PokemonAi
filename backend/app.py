from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import answer_question, search_knowledge


app = FastAPI(title="Poképilot AI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Poképilot AI backend is running.",
        "docs": "/docs",
        "ask_endpoint": "/ask",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_pokemon_ai(request: AskRequest):
    if not request.question.strip():
        return {
            "answer": "Please ask a Pokémon question.",
            "sources": [],
        }

    return answer_question(request.question)


@app.post("/search")
def search_pokemon_knowledge(request: AskRequest):
    if not request.question.strip():
        return {"results": []}

    return {"results": search_knowledge(request.question)}
