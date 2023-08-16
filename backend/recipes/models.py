from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название тэга",
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет в HEX",
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Введенное значение не является цветом в формате HEX!",
            )
        ],
    )
    slug = models.SlugField(
        verbose_name="Уникальный слаг",
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        "Ингридиент",
        max_length=200,
    )
    measurement_unit = models.CharField(
        "Единицы измерения",
        max_length=24,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_for_ingredient"
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
    )
    name = models.CharField(verbose_name="Название блюда", max_length=125)
    image = models.ImageField(
        verbose_name="Изображения блюда", upload_to="recipes/image/"
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name="Ингридиенты",
        through="AmountIngredient",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэг",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время готовки", default=0
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("author",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "author"),
                name="unique_for_author",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="amount_ingredient",
        verbose_name="В каких рецептах",
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredients,
        verbose_name="Связанные ингредиенты",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Количество ингридиентов"
        ordering = ("recipe",)
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "ingredients",
                ),
                name="unique_ingredients_recipe",
            ),
        ]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Понравившиеся рецепты",
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Пользователь",
        related_name="favorite",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="unique_favorite_recipe_for_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"


class ShoppingСart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепты в списке покупок",
        related_name="shopping_cart",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Владелец списка",
        related_name="shopping_cart",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="unique_cart_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"
