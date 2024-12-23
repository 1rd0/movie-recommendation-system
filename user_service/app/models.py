from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)

    def __str__(self):
        return f"User {self.email}"


class UserProfile(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="profile")
    name = fields.CharField(max_length=255)
    preferences = fields.CharField(max_length=255, null=True)
