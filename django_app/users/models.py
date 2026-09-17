# django_app/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # AbstractUser already provides: id, username, password, email, date_joined
    # We just ensure the fields are configured as needed.
    # Note: AbstractUser.email is not unique by default, we override that.
    email = models.EmailField(unique=True)
    
    # Override created_at to match other frameworks (AbstractUser uses date_joined)
    # For benchmarking parity, we'll alias or use date_joined, but let's add explicit created_at if strict parity is needed.
    # However, for simplicity in Django, 'date_joined' is the standard equivalent.
    # Let's stick to standard Django fields to remain idiomatic, but map 'date_joined' to 'created_at' in serializers later.
    
    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username