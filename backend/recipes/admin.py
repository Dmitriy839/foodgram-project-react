from django.contrib import admin
from django.contrib.admin import display

from .models import Favorite, Ingredients, Recipe, ShoppingСart, Tag, AmountIngredient


class IngredientsInLine(admin.TabularInline):
    model = AmountIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "author", "added_in_favorite")
    search_fields = ("name", "author__username")
    list_filter = (
        "author",
        "name",
        "tags",
    )
    inlines = (IngredientsInLine,)

    @display(description="Количество в избранных")
    def added_in_favorite(self, obj):
        return obj.favorite.count()


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    search_fields = ("name", "slug")


@admin.register(ShoppingСart)
class CartsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user__username", "user__email")


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    search_fields = ("user__username", "user__email")
