from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        verbose_name=_('e-mail'),
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name=_('username'),
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=150,
        blank=False,
        null=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name'
    ]

    class Meta:
        ordering = ['-pk']
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('follower'),
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('following'),
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('follow')
        verbose_name_plural = _('follows')
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='%(app_label)s_%(class)s_unique',
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='%(app_label)s_%(class)s_prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.follower.username} follow {self.following.username}'
