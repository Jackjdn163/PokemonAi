import argparse
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from sources import (
    fetch_pokemon_data,
    fetch_move_data,
    fetch_ability_data,
)


DB_PATH = "./data/chroma"


def main():
    parser = argparse.ArgumentParser(description="Build the Poképilot AI knowledge database.")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Build a smaller test database first. Good for checking that everything works.",
    )
    args = parser.parse_args()

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name="pokemon_knowledge",
        embedding_function=embedding_function,
    )

    docs = []

    if args.quick:
        print("Running quick ingest. This only downloads a small amount of data.")
        docs.extend(fetch_pokemon_data(limit=50))
        docs.extend(fetch_move_data(limit=100))
        docs.extend(fetch_ability_data(limit=50))
    else:
        print("Running full ingest. This may take a while the first time.")
        docs.extend(fetch_pokemon_data(limit=1025))
        docs.extend(fetch_move_data())
        docs.extend(fetch_ability_data())

    print(f"Adding {len(docs)} documents to ChromaDB...")

    collection.upsert(
        ids=[doc["id"] for doc in docs],
        documents=[doc["text"] for doc in docs],
        metadatas=[{"source": doc["source"], "title": doc["title"]} for doc in docs],
    )

    print("Done. Pokémon AI database created.")


if __name__ == "__main__":
    main()
