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
