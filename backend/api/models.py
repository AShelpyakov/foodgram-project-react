from django.db import models
from django.utils.translation import gettext_lazy as _


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name=_('ingredient name'),
        max_length=200,
        blank=False,
        null=False,
        unique=True,
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
