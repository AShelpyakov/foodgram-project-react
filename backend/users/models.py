from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        null=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name'
    ]

    class Meta:
        ordering = ('-pk',)


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='%(app_label)s_%(class)s_unique',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='%(app_label)s_%(class)s_prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.follower.username} follow {self.following.username}'
