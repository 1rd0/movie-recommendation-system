# app/models.py
from typing import Optional, List
from pydantic import BaseModel

class MovieCreate(BaseModel):
    type: str
    title: str
    director: str
    cast: str
    release_year: str
    genres: str
    description: str

    def create_textual_representation(self):
        return f"""Type: {self.type},
Title: {self.title},
Director: {self.director},
Cast: {self.cast},
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
Cast: {self.cast or ''},
Released: {self.release_year or ''},
Genres: {self.genres or ''},

Description: {self.description or ''}"""
