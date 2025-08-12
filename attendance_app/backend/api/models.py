# api/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("L'utilisateur doit avoir un nom d'utilisateur")
        user = self.model(username=username)
        user.set_password(password)  # Définit le mot de passe haché
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)  # Nom d'utilisateur
    password = models.CharField(max_length=128)  # Mot de passe haché

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Pas d'autres champs requis

    objects = CustomUserManager()

    def __str__(self):
        return self.user