# app/services/index.py
import faiss
import numpy as np
from fastapi import HTTPException
from app.config import FAISS_INDEX_PATH, DIM
from app.services.embeddings import get_embedding_from_ollama
from datetime import datetime

try:
    index = faiss.read_index(FAISS_INDEX_PATH)
    print("FAISS index loaded successfully")
except Exception as e:
    print(f"Failed to load FAISS index from {FAISS_INDEX_PATH}: {e}")
    raise HTTPException(status_code=500, detail="Failed to load FAISS index")

async def compute_user_profile_embedding(user_history, movie_metadata, current_date=None, lambda_=0.01):
    user_embedding = np.zeros(DIM, dtype="float32")
    total_weight = 0
    if current_date is None:
        current_date = datetime.now()

    for entry in user_history:
        movie_id = entry["movie_id"]
        rating = entry["rating"]
        watched_at = datetime.fromisoformat(entry["watched_at"])

        if movie_id not in movie_metadata:
            continue

        movie = movie_metadata[movie_id]
        if not isinstance(movie, dict) or "textual_representation" not in movie:
            continue
        
        prompt = movie["textual_representation"]
        embedding = await get_embedding_from_ollama(prompt)

        if embedding is None:
            print(f"Skipping movie_id {movie_id} because no embedding was found.")
            continue

        time_diff = (current_date - watched_at).days
        time_weight = np.exp(-lambda_ * time_diff)
        weight = rating * time_weight
        user_embedding += embedding * weight
        total_weight += weight

    if total_weight > 0:
        user_embedding /= total_weight
    else:
        print("No valid embeddings were found for user profile, returning zero vector.")

    return user_embedding

def search_similar(user_profile_embedding, k=3):
    user_profile_embedding = user_profile_embedding.reshape(1, -1)
    D, I = index.search(user_profile_embedding, k)
    return I.flatten()
