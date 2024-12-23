# app/models.py
from typing import Optional, List
from pydantic import BaseModel
from tortoise import fields, models

class Movie(models.Model):
    id = fields.IntField(pk=True)
    type = fields.CharField(max_length=50)
    title = fields.CharField(max_length=255) 
    director = fields.CharField(max_length=255, null=True)
    cast_members = fields.TextField(null=True)
    release_year = fields.CharField(max_length=40, null=True)
    genres = fields.TextField(null=True)
    description = fields.TextField(null=True)
    textual_representation = fields.TextField(null=True)

    def __str__(self):
        return self.title
 
class Review(models.Model):
    id = fields.IntField(pk=True)
    movie = fields.ForeignKeyField("models.Movie", related_name="reviews")  
    user_id = fields.IntField()  
    rating = fields.IntField()   
    review_text = fields.TextField(null=True)   
    created_at = fields.DatetimeField(auto_now_add=True)   

    def __str__(self):
        return f"Review for {self.movie.title} by User {self.user_id}"

class MovieCreate(BaseModel):
    type: str
    title: str
    director: str
    cast_members: str   
    release_year: str
    genres: str
    description: str

    def create_textual_representation(self):
        return f"""Type: {self.type},
Title: {self.title},
Director: {self.director},
Cast: {self.cast_members},  # Обновлено для соответствия
Released: {self.release_year},
Genres: {self.genres},

Description: {self.description}"""

class MovieUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[str] = None
    release_year: Optional[str] = None
    genres: Optional[str] = None
    description: Optional[str] = None

    def create_textual_representation(self):
        return f"""Type: {self.type or ''},
Title: {self.title or ''},
Director: {self.director or ''},
Cast: {self.cast_members or ''},
Released: {self.release_year or ''},
Genres: {self.genres or ''},

Description: {self.description or ''}"""
