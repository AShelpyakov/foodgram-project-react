from django.db import models
from django.utils.translation import gettext_lazy as _


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_('ingredient name'),
        max_length=200,
        blank=False,
        null=False,
    )
    measurement_unit = models.CharField(
        verbose_name=_('measurement unit'),
        max_length=200,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='%(app_label)s_%(class)s_unique',
            ),
        ]


class Tag(models.Model):
    name = models.CharField(
        verbose_name=_('tag name'),
        max_length=200,
        blank=False,
        null=False,
        unique=True
    )
    color = models.CharField(
        verbose_name=_('tag color'),
        max_length=7,
        blank=False,
        null=True,
    )
    slug = models.SlugField(
        verbose_name=_('tas slug'),
        max_length=200,
        blank=False,
        null=True,
        unique=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')