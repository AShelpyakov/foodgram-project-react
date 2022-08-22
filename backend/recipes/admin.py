from django.contrib import admin
from django.contrib.admin import display
from django.utils.translation import gettext_lazy as _

from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'recipe_favorite_count')
    list_filter = ('author__email', 'name', 'tags__name')
    search_fields = ('author__email', 'name', 'tags__name')

    def recipe_favorite_count(self, obj):
        return obj.favorite_set.count()


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
