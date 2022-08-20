from django.db.models import Sum
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from .filters import IngredientSearchFilter, RecipeFilter
from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Tag,
)
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShoppingCartSerializer, TagSerializer,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=('post',)
    )
    def favorite(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = request.user
        try:
            favorite = Favorite.objects.get(user=user, recipe=pk)
        except Favorite.DoesNotExist:
            return Response(
                {'error': _('the recipe is not in favorites')},
                status=HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=('post',)
    )
    def shopping_cart(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = request.user
        try:
            shopping_cart = ShoppingCart.objects.get(user=user, recipe=pk)
        except ShoppingCart.DoesNotExist:
            return Response(
                {'error': _('the recipe is not in shopping cart')},
                status=HTTP_400_BAD_REQUEST,
            )
        shopping_cart.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_text_shopping_cart(self, ingredients):
        shopping_cart = _('shopping cart:') + '\n'
        for ingredient in ingredients:
            shopping_cart += (
                    f'{ingredient["ingredient__name"]} - '
                    + f'{ingredient["total_amount"]}'
                    + f'{ingredient["ingredient__measurement_unit"]}.'
                    + '\n'
            )
        return shopping_cart

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        methods=('get',)
    )
    def download_shopping_cart(self, request):
        user = request.user
        values_list = ('ingredient__name', 'ingredient__measurement_unit')
        ingredients = RecipeIngredients.objects.filter(
            recipe__shoppingcart__user=user
        ).values(*values_list).annotate(
            total_amount=Sum('amount')
        ).order_by(*values_list)

        response = HttpResponse(
            self.get_text_shopping_cart(ingredients),
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': (
                    'attachment; filename="shopping_cart.txt"'
                ),
            },
        )
        return response
