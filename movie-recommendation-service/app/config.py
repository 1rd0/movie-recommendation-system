# app/config.py

FAISS_INDEX_PATH = "E:/movie-recommendation-system/recommendation_service/index.faiss"
DIM = 1024  # Размерность векторов

USER_SERVICE_URL = "http://localhost:8000"
MOVIE_SERVICE_URL = "http://localhost:8001"
EMBEDDING_SERVICE_URL = "http://localhost:11434/api/embeddings"
DEFAULT_NUM_RECOMMENDATIONS = 3
