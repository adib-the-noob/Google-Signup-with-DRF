from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,
    PermissionsMixin
)

class UserManager(BaseUserManager):

    def create_user(self, email, username, full_name, password, **other_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            full_name=full_name,
            is_active=True,
            **other_fields
        )

        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')

        superUser = self.model(username=username, **other_fields)
        superUser.set_password(password)
        superUser.save()
        return superUser


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    username = models.CharField(max_length=13, unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
   
    objects = UserManager()     

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username