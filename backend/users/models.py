from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=254,
        unique=True,
        help_text="Адрес электронной почты",
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=32,
        unique=True,
        help_text="Укажите Логин",
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=32, help_text="Укажите Имя"
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=32, help_text="Укажите Фамилию"
    )

    class Meta:
        ordering = ("username",)

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        related_name="subscribers",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Подписчики",
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="Дата создания подписки",
        auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("author", "user"), name="unique_subscription"
            )
        ]
