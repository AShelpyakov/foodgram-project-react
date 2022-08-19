from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import SubscribedUserSerializer

from .constants import INGREDIENT_MIN_AMOUNT
from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag,
)
from .shared_serializers import ShortRecipeSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe, context={'request': request}
        ).data

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'status': _('the recipe is already in favorites')}
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe, context={'request': request}
        ).data

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'status': _('the recipe is already in shopping cart')}
            )
        return data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = SubscribedUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'id', 'author', 'name', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'image', 'tags', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = obj.recipeingredients_set.all()
        return RecipeIngredientsSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj,
        ).exists()


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientWriteSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
        )

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_object = Ingredient.objects.get(id=ingredient.get('id'))
            recipe.ingredients.add(
                ingredient_object,
                through_defaults={'amount': amount}
            )

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            self.create_tags(tags, recipe)
            self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        instance.tags.clear()
        tags = validated_data.get('tags')
        with transaction.atomic():
            self.create_tags(tags, instance)
            RecipeIngredients.objects.filter(recipe=instance).all().delete()
            ingredients = validated_data.get('ingredients')
            self.create_ingredients(ingredients, instance)
            instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def validate(self, data):
        if len(data['tags']) == 0:
            raise ValidationError(_('Must be minimum one tag'))
        if len(data['tags']) > len(set(data['tags'])):
            raise ValidationError(_('Tags must be not identical'))
        if len(data['ingredients']) == 0:
            raise ValidationError(_('Must be minimum one ingredient'))
        ingredients = []
        for ingredient in data['ingredients']:
            if ingredient['amount'] < INGREDIENT_MIN_AMOUNT:
                raise ValidationError(
                    _('Amount must be equal or more then ')
                    + f'{INGREDIENT_MIN_AMOUNT}'
                )
            ingredients.append(ingredient['id'])
        if len(ingredients) > len(set(ingredients)):
            raise ValidationError(_('Ingredients must be not identical'))
        return data
