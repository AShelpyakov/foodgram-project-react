from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.shared_serializers import ShortRecipeSerializer

from .models import Follow

User = get_user_model()


class SubscribedUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            follower=request.user, following=obj
        ).exists()


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(
            follower=request.user, following=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                raise serializers.ValidationError(
                    _('recipe_limit must be integer'),
                )
        recipes = obj.recipe_set.all()[:recipes_limit]
        return ShortRecipeSerializer(
            recipes, many=True, context=context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipe_set.count()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('follower', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=fields,
                message=_('You are already subscribed to this author'),
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        following = data['following']
        if request.user == following:
            raise serializers.ValidationError(
                _('You can not subscribe to yourself'),
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowListSerializer(
            instance.following, context=context
        ).data
