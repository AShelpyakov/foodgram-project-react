from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


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
                1, message=_('Time must be more then 0')
            )
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')


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
            MinValueValidator(1, message=_('Amount must be more then 0'))
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
