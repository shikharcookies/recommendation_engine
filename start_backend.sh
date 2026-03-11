#!/bin/bash

echo "Starting Counterparty Recommendation Engine Backend..."
echo ""
echo "Make sure you have:"
echo "1. Installed dependencies: pip install -r requirements.txt"
echo "2. Downloaded spacy model: python -m spacy download en_core_web_sm"
echo "3. Created .env file with OPENROUTER_API_KEY"
echo ""
echo "Starting server at http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload
