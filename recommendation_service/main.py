import pandas as pd
import requests
import faiss
import numpy as np

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
#X = np.zeros((len(df['textual_representation']), dim), dtype='float32')

# Функция для получения эмбеддингов через HTTP API с таймаутом
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

# Заполняем матрицу эмбеддингами
#for i, prompt in enumerate(df['textual_representation']):
    if i % 30 == 0:
        print(f'Processed {i} instances')
    embedding = get_embedding_from_ollama(prompt)
    if embedding is not None:
        X[i] = embedding

# Добавляем вектора в FAISS индекс и сохраняем его
# index.add(X)
# faiss.write_index(index, 'E:/movie-recommendation-system/recommendation_service/index.faiss')  # Измените путь на верный

# Загружаем индекс (можно загружать по мере необходимости)
index = faiss.read_index('E:/movie-recommendation-system/recommendation_service/index.faiss')  # Измените путь на верный

### Функция для получения усредненного вектора на основе истории пользователя
def get_user_profile_embedding(user_history, df):
    """
    user_history - список кортежей вида (movie_id, rating)
    """
    user_embedding = np.zeros(dim, dtype='float32')
    total_weight = 0

    for movie_id, rating in user_history:
        # Получаем текстовое представление и эмбеддинг фильма
        prompt = df.iloc[movie_id]['textual_representation']
        embedding = get_embedding_from_ollama(prompt)
        if embedding is not None:
            user_embedding += embedding * rating
            total_weight += rating

    # Усредняем вектор, если есть вес
    if total_weight > 0:
        user_embedding /= total_weight

    return user_embedding

# Пример истории пользователя: (movie_id, rating)
user_history = [(332, 5), (323, 5), (431, 5), (222, 5), (112, 5)]

# Получаем усредненный вектор предпочтений пользователя
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
