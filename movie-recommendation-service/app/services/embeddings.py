# app/services/embeddings.py
import aiohttp
import numpy as np
from app.config import EMBEDDING_SERVICE_URL

async def get_embedding_from_ollama(prompt: str) -> np.ndarray:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                EMBEDDING_SERVICE_URL,
                json={"model": "mxbai-embed-large", "prompt": prompt},
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if "embedding" in data:
                    return np.array(data["embedding"], dtype="float32")
                else:
                    print(f"Embedding not found in response for prompt: {prompt}")
                    return None
    except Exception as e:
        print(f"Error fetching embedding for prompt: {prompt} - Error: {e}")
        return None
