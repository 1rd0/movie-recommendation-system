# app/config.py

FAISS_INDEX_PATH = "E:/movie-recommendation-system/movie-recommendation-service/recommendation_service/index.faiss"
DIM = 1024  
RABBITMQ_URL = "amqp://rmuser:rmpassword@localhost:5672/"
EMEIL_SERVICE_URL="http://localhost:8000"
USER_SERVICE_URL = "http://localhost:8001"
MOVIE_SERVICE_URL = "http://localhost:8002"
EMBEDDING_SERVICE_URL = "http://localhost:11434/api/embeddings"
DEFAULT_NUM_RECOMMENDATIONS = 3
TORTOISE_ORM = {
    "connections": {
        
        "default": "postgres://postgres:postgres@localhost:5433/recdatabase"
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],   
            "default_connection": "default",
        }
    },
}