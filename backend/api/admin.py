from django.contrib import admin
from django.contrib.admin import display
from django.utils.translation import gettext_lazy as _

from .models import (
    Ingredient, Favorite, Recipe,
    RecipeIngredients, Tag, ShoppingCart,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    list_filter = ('author', 'tags')
    search_fields = ('author__email', 'name', 'tags__name')


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ingredient', 'recipe',
        'get_measurement_unit', 'amount',
    )
    list_filter = ('ingredient',)
    search_fields = ('ingredient__name', 'recipe__name')

    @display(description=_('measurement unit'))
    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user__email', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user__email', 'recipe__name')
