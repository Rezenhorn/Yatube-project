from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    """Модель групп."""
    title = models.CharField(
        verbose_name="Название",
        help_text="Укажите название группы",
        max_length=200)
    slug = models.SlugField(
        verbose_name="Адрес",
        help_text="Укажите уникальный адрес группы, часть URL",
        unique=True)
    description = models.TextField(
        verbose_name="Описание",
        help_text="Укажите общую информацию о группе"
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель постов."""
    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст поста",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        db_index=True)
    group = models.ForeignKey(
        Group,
        verbose_name="Группа",
        help_text="Группа, к которой относится пост",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts"
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        help_text="Автор поста",
        on_delete=models.CASCADE,
        related_name="posts"
    )
    image = models.ImageField(
        "Картинка",
        help_text="Изображение, прикрепленное к посту",
        upload_to="posts/",
        blank=True
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]  # Первые 15 символов поста.


class Comment(models.Model):
    """Модель комментариев."""
    post = models.ForeignKey(
        Post,
        verbose_name="Пост",
        help_text="Пост, к которому оставлен коммент",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        help_text="Автор комментария",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст комментария",
    )
    created = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:15]  # Первые 15 символов коммента.


class Follow(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_follow",
            ),
        ]

    def __str__(self):
        return f"{self.user} follows {self.author}"
