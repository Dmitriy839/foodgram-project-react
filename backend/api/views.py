from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    CustomUserSerializer,
    RecipeSerializer,
    SubscribeSerializer,
    RecipeCreateSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    FavoriteSerializer,
)
from users.models import Subscriptions
from recipes.models import (
    Favorite,
    Ingredients,
    AmountIngredient,
    Recipe,
    ShoppingСart,
    Tag
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        data = {
            'user': request.user.id,
            'author': self.kwargs.get('id')
        }

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscriptions,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribers__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorAdminOrReadOnly, )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'amount_ingredient__ingredients', 'tags'
        )
        return recipes

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def send_message(ingredients):
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredients__name']} "
                f"({ingredient['ingredients__measurement_unit']}) - "
                f"{ingredient['amount']}"
            )
        file = 'shopping_list'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(
        detail=False,
        methods=['GET']
    )
    def download_shopping_cart(self, request):
        ingredients = AmountIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredients__name').values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user.id,
            'recipe': recipe.id
        }
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data=data,
                context=context,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            is_shopping_cart = get_object_or_404(Favorite, user=user, recipe=recipe)
            is_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        user = request.user
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user.id,
            'recipe': recipe.id
        }
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data=data,
                context=context,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            is_shopping_cart = get_object_or_404(ShoppingСart, user=user, recipe=recipe)
            is_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
