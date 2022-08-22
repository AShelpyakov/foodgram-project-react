from autoslug import AutoSlugField
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import (
    COLOR_PALETTE, COOKING_TIME_MIN_VALUE, INGREDIENT_MIN_AMOUNT,
)

User = get_user_model()


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

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name=_('tag name'),
        max_length=200,
        blank=False,
        null=False,
        unique=True
    )
    color = ColorField(
        default='#FF0000',
        samples=COLOR_PALETTE,
        verbose_name=_('tag color'),
        blank=False,
        null=False,
    )
    slug = AutoSlugField(
        populate_from='name',
        verbose_name=_('tag slug'),
        max_length=200,
        blank=False,
        null=True,
        unique=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name=_('recipe name'),
        max_length=200,
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('tags'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('author'),
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name=_('list ingredients'),
        through='RecipeIngredients',
    )
    image = models.ImageField(
        verbose_name=_('recipe image'),
    )
    text = models.TextField(
        verbose_name=_('recipe text'),
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('cooking time in minutes'),
        validators=[
            MinValueValidator(
                COOKING_TIME_MIN_VALUE,
                message=_('Time must be equal or more then 1'),
            )
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('ingredient'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('recipe'),
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=_('amount'),
        validators=[
            MinValueValidator(
                INGREDIENT_MIN_AMOUNT,
                message=_('Amount must be equal or more then 1'),
            )
        ],
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='%(app_label)s_%(class)s_unique',
            )
        ]
        verbose_name = _('recipe ingredient')
        verbose_name_plural = _('recipe ingredients')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('recipe'),
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique',
            )
        ]
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('recipe'),
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique',
            )
        ]
        verbose_name = _('shopping cart')
        verbose_name_plural = _('shopping carts')
