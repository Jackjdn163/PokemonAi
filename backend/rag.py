import os
from typing import Dict, List

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

DB_PATH = "./data/chroma"
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client_db = chromadb.PersistentClient(path=DB_PATH)

collection = client_db.get_or_create_collection(
    name="pokemon_knowledge",
    embedding_function=embedding_function,
)


def search_knowledge(question: str, results: int = 8) -> List[Dict[str, str]]:
    search_results = collection.query(
        query_texts=[question],
        n_results=results,
    )

    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]

    chunks = []

    for doc, meta in zip(documents, metadatas):
        chunks.append({
            "title": meta.get("title", "Unknown"),
            "source": meta.get("source", "Unknown"),
            "text": doc,
        })

    return chunks


def answer_question(question: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "answer": "Missing OPENAI_API_KEY. In Codespaces, create backend/.env from .env.example and paste your API key.",
            "sources": [],
        }

    chunks = search_knowledge(question)

    if not chunks:
        return {
            "answer": "I could not find anything in the Pokémon knowledge database. Run `python ingest.py --quick` first.",
            "sources": [],
        }

    context = "\n\n".join(
        [
            f"Source: {chunk['source']}\nTitle: {chunk['title']}\nInfo: {chunk['text']}"
            for chunk in chunks
        ]
    )

    prompt = f"""
You are Poképilot AI, a helpful Pokémon assistant for casual single-player Pokémon players.

Use ONLY the provided context.
If the answer is not in the context, say that you do not have enough information from the current database.
Do not pretend to know things that are not in the context.
Be clear, useful, and beginner-friendly.
When helpful, give simple steps.

User question:
{question}

Context:
{context}
"""

    ai_client = OpenAI(api_key=api_key)

    response = ai_client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a reliable Pokémon assistant for casual single-player players.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [
            {
                "title": chunk["title"],
                "source": chunk["source"],
            }
            for chunk in chunks
        ],
    }
