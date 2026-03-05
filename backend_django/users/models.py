from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
