from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'


class UserManager(BaseUserManager):
    """Manager for the User model"""

    def create_user(self, email, username, **extra_fields):
        if not email:
            raise ValueError('Enter your email')
        if not username:
            raise ValueError('Enter your username')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Enter your email')
        if not username:
            raise ValueError('Enter your username')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            is_staff=True,
            is_superuser=True,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """Custom user model."""
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]

    email = models.EmailField(
        max_length=254,
        verbose_name='Email',
        unique=True,
        blank=False,
        null=False
    )

    username = models.CharField(
        verbose_name='Username',
        max_length=50,
        unique=True)

    first_name = models.CharField(
        max_length=150,
        verbose_name='Name',
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Last name',
        blank=True,
    )

    bio = models.TextField(
        verbose_name='Description',
        max_length=500,
        blank=True,
    )

    role = models.CharField(
        max_length=10,
        verbose_name='User type',
        choices=ROLE_CHOICES,
        default=USER,
    )

    confirmation_code = models.UUIDField(
        verbose_name='Confirmation code',
        default=0,
        editable=False,
    )

    def is_moderator(self):
        return self.role == 'moderator'

    def is_admin(self):
        return self.role == 'admin'

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('username',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'
