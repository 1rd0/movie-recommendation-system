import pandas as pd
import asyncpg
import asyncio

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/postgres"

async def import_movies():
    # Load CSV file
    df = pd.read_csv("E:/movie-recommendation-system/recommendation_service/netflix_titles.csv")
    
    # Replace NaN values with an empty string
    df.fillna("", inplace=True)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Clear the movies table (optional)
    await conn.execute("TRUNCATE TABLE movies")
    
    # Insert data into the database
    for _, row in df.iterrows():
        await conn.execute(
            """
            INSERT INTO movies (type, title, director, cast_members, release_year, genres, description)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            row['type'],
            row['title'],
            row['director'],
            row['cast'],
            row['release_year'],
            row['listed_in'],
            row['description']
        )
    
    await conn.close()
    print("Data import completed.")

if __name__ == "__main__":
    asyncio.run(import_movies())
