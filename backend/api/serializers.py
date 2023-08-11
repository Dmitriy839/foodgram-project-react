from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredients, AmountIngredient, Recipe,
                            ShoppingСart, Tag)
from rest_framework.fields import SerializerMethodField, ReadOnlyField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from users.models import Subscriptions

User = get_user_model()


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class SubscriptionSerializer(ModelSerializer):

    class Meta:
        model = Subscriptions
        fields = ('user', 'author')

    def to_representation(self, instance):
        return SubscribeSerializer(instance.user, context={
            'request': self.context.get('request')
        }).data


class SubscribeSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortResipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredients.id')
    name = ReadOnlyField(source='ingredients.name')
    measurement_unit = ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='amount_ingredient'
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingСart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class RecipeIngredientCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredients',
        queryset=Ingredients.objects.all()
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'tags',
            'ingredients',
            'text',
            'image',
            'cooking_time'
        )

    def create_ingredients(self, ingredient, instance):
        for ingredient_data in ingredient:
            AmountIngredient.objects.create(
                recipe=instance,
                ingredients=ingredient_data['ingredients'],
                amount=ingredient_data['amount']
            )

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        self.create_ingredients(ingredient, instance)
        return instance

    def update(self, instance, validated_data):
        ingredient = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        AmountIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredient, instance)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShortResipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(ModelSerializer):

    class Meta:
        model = ShoppingСart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShortResipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
