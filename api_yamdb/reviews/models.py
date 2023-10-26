from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

SCORE_CHOICES = (
    (1, '1 - Отвратительно'),
    (2, '2 - Очень плохо'),
    (3, '3 - Плохо'),
    (4, '4 - Скорее плохо'),
    (5, '5 - Средне'),
    (6, '6 - Неплохо'),
    (7, '7 - Скорее хорошо'),
    (8, '8 - Хорошо'),
    (9, '9 - Очень хорошо'),
    (10, '10 - Великолепно')
)

USER_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class CommentsAndReviews(models.Model):
    """Модели Комментарии Отзывы."""
    text = models.TextField('Текст',)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class CategoryAndGenre(models.Model):
    """Модели Категория Жанр."""
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField('Почта', unique=True)
    bio = models.TextField('Инфо', blank=True)
    role = models.CharField('Роль',
                            max_length=16,
                            choices=USER_CHOICES,
                            default='user')
    confirmation_code = models.CharField('Код подтверждения',
                                         max_length=150,
                                         default='NewCode')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_staff or self.role == settings.ADMIN

    @property
    def is_moderator(self):
        return self.role == settings.MODERATOR


class Category(CategoryAndGenre):
    """Содержит данные о категориях произведений."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryAndGenre):
    """Содержит данные о жанрах произведений."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Содержит данные о произведениях."""
    name = models.CharField('Название', max_length=256)
    year = models.IntegerField('Год создания', )
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(
        Genre,
        # null=True,
        # blank=True,
        # through='TitleGenre',
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year',)

    def __str__(self):
        return self.name


# class TitleGenre(models.Model):
#     """Служит для обеспечения связей многие-ко-многим."""
#     title = models.ForeignKey(Title, on_delete=models.CASCADE)
#     genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f'{self.title} {self.genre}'


class Review(CommentsAndReviews):
    """Содержит пользовательские отзывы о произведениях."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField('Оценка', choices=SCORE_CHOICES)
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'
            )
        ]


class Comment(models.Model):
    """Комментарии."""
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    text = models.TextField('Комментарий')
    pub_date = models.DateTimeField(
        'Дата',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.text
