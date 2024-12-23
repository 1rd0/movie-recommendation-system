import pandas as pd
import asyncpg
import asyncio

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/moviedatabase"

# Функция для создания текстового представления
def create_textual_representation(row):
    # Проверим, что все необходимые поля не пусты
    if not row['type'] or not row['title']:
        return ""  # если каких-то данных нет, возвращаем пустую строку или подходящее значение по умолчанию
    return f"""Type: {row['type']},
Title: {row['title']},
Director: {row['director']},
Cast: {row['cast']},
Released: {row['release_year']},
Genres: {row['listed_in']}, 

Description: {row['description']}"""

async def import_movies():
    # Загружаем CSV файл
    df = pd.read_csv("E:/movie-recommendation-system/3/netflix_titles.csv")
    
    # Заполняем пропуски значениями ""
    df.fillna("", inplace=True)
    
    # Преобразуем ст    лбец release_year в строки
    df['release_year'] = df['release_year'].astype(str)
    
    # Добавляем колонку textual_representation
    df['textual_representation'] = df.apply(create_textual_representation, axis=1)
    
    # Создаем соединение с базой данных
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Очистим таблицу movies (опционально)
    await conn.execute("TRUNCATE TABLE movie")
    
    # Вставляем данные в базу данных
    for _, row in df.iterrows():
        await conn.execute(
            """
            INSERT INTO movie (type, title, director, cast_members, release_year, genres, description, textual_representation)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            row['type'],
            row['title'],
            row['director'],
            row['cast'],
            row['release_year'],  # Убедились, что передаем строку
            row['listed_in'],
            row['description'],
            row['textual_representation']  # Добавляем новое поле
        )
    
    await conn.close()
    print("Data import completed.")

if __name__ == "__main__":
    asyncio.run(import_movies())
