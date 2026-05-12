#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Building a quick test Pokémon database..."
python ingest.py --quick

echo "Starting FastAPI server..."
uvicorn app:app --host 0.0.0.0 --port 8000
