from tortoise.models import Model
from tortoise import fields
from tortoise.fields import DatetimeField
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)
 
 
class UserHistory(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()  # Храним ID пользователя вместо внешнего ключа
    movie_id = fields.IntField()
    rating = fields.IntField()
    watched_at = DatetimeField(default=utc_now)

from tortoise.models import Model
from tortoise import fields

from tortoise.models import Model
from tortoise import fields

class Review(Model):
    id = fields.IntField(pk=True)
    movie_id = fields.IntField()  # ID фильма из внешней базы данных
    user_id = fields.IntField()
    rating = fields.IntField()
    review_text = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for movie_id {self.movie_id} by User {self.user_id}"
