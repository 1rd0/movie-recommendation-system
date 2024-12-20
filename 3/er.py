 

import pandas as pd
import requests
import faiss
import numpy as np
from datetime import datetime

# Загрузка данных из CSV
df = pd.read_csv("E:/movie-recommendation-system/recommendation_service/netflix_titles.csv")  # Измените путь на правильный для Windows

# Функция для создания текстового представления
def create_textual_representation(row):
    return f"""Type: {row['type']},
Title: {row['title']},
Director: {row['director']},
Cast: {row['cast']},
Released: {row['release_year']},
Genres: {row['listed_in']},

Description: {row['description']}"""

df['textual_representation'] = df.apply(create_textual_representation, axis=1)

# Настройка FAISS
dim = 1024
index = faiss.IndexFlatL2(dim)

def get_embedding_from_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={'model': 'mxbai-embed-large', 'prompt': prompt},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        if 'embedding' in data:
            return np.array(data['embedding'], dtype='float32')
        else:
            print("Ошибка: 'embedding' не найден в ответе:", data)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обращении к серверу Ollama: {e}")
        return None

# Пример: загрузка индекса
index = faiss.read_index('E:/movie-recommendation-system/recommendation_service/index.faiss')  # Измените путь на верный

### Функция для получения вектора предпочтений пользователя с учетом времени просмотра
def get_user_profile_embedding(user_history, df, current_date=None, lambda_=0.01):
    """
    user_history - список кортежей (movie_id, rating, watched_at)
    current_date - текущая дата для вычисления давности (datetime)
    lambda_ - коэффициент экспоненциального затухания по времени
    """
    user_embedding = np.zeros(dim, dtype='float32')
    total_weight = 0

    if current_date is None:
        # Если текущая дата не указана, берем сегодняшнюю
        current_date = datetime.now()

    for movie_id, rating, watched_at in user_history:
        prompt = df.iloc[movie_id]['textual_representation']
        embedding = get_embedding_from_ollama(prompt)
        if embedding is not None:
            # Преобразуем watched_at к datetime, если это строка
            if isinstance(watched_at, str):
                watched_at_date = datetime.fromisoformat(watched_at)
            else:
                watched_at_date = watched_at
            
            # Рассчитываем разницу по времени (например, в днях)
            time_diff = (current_date - watched_at_date).days
            
            # Вычисляем вес по времени
            # Чем давнее, тем меньше вес. Например, экспоненциальный спад:
            time_weight = np.exp(-lambda_ * time_diff)
            
            # Итоговый вес = рейтинг * time_weight
            weight = rating * time_weight
            
            user_embedding += embedding * weight
            total_weight += weight

    # Усредняем вектор, если есть вес
    if total_weight > 0:
        user_embedding /= total_weight

    return user_embedding


# Пример истории пользователя: (movie_id, rating, watched_at)
# Предполагается, что watched_at в формате ISO-8601: 'YYYY-MM-DD'
user_history = [
    (532, 5, '2024-12-15 21:14:40.048515'),
    (523, 5, '2024-12-15 21:14:50.724527'),
    (531, 3, '2024-12-15 21:30:22.624318'),
    (522, 5, '2024-12-16 10:40:10.154194'),
   
]

# Получаем усредненный вектор предпочтений пользователя с учетом времени просмотра
user_profile_embedding = get_user_profile_embedding(user_history, df)

# Выполняем поиск похожих фильмов на основе профиля пользователя
if user_profile_embedding is not None:
    user_profile_embedding = user_profile_embedding.reshape(1, -1)
    D, I = index.search(user_profile_embedding, 5)
    best_matches = df.iloc[I.flatten()]
    
    # Выводим рекомендации
    print("Рекомендации на основе истории пользователя:")
    for _, row in best_matches.iterrows():
        print(f"Title: {row['title']}, Type: {row['type']}, Year: {row['release_year']}")
        print(f"Genres: {row['listed_in']}")
        print(f"Description: {row['description']}\n")
  