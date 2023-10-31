import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import UsernameValidator, check_username_me

LENGTH_SHORT = 30
MAX_LENGTH = 256
AVERAGE = 150
DEFAULT_CODE = 'NewCode'

# SCORE_CHOICES = (
#     (1, '1 - Отвратительно'),
#     (2, '2 - Очень плохо'),
#     (3, '3 - Плохо'),
#     (4, '4 - Скорее плохо'),
#     (5, '5 - Средне'),
#     (6, '6 - Неплохо'),
#     (7, '7 - Скорее хорошо'),
#     (8, '8 - Хорошо'),
#     (9, '9 - Очень хорошо'),
#     (10, '10 - Великолепно')
# )


class CommentsAndReviews(models.Model):
    """Комментарии Отзывы."""

    text = models.TextField('Текст',)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:LENGTH_SHORT]


class CategoryAndGenre(models.Model):
    """Категория Жанр."""

    name = models.CharField('Название', max_length=MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:LENGTH_SHORT]


class User(AbstractUser):
    """Пользователи."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    USER_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField('Почта', unique=True)
    bio = models.TextField('Инфо', blank=True)
    role = models.CharField('Роль',
                            max_length=max([
                                len(pos) for pos, _ in USER_CHOICES]),
                            choices=USER_CHOICES,
                            default=USER)
    confirmation_code = models.CharField('Код подтверждения',
                                         max_length=AVERAGE,
                                         default=DEFAULT_CODE)
    username = models.CharField(
        'Имя пользователя',
        validators=(UsernameValidator(), check_username_me),
        max_length=AVERAGE,
        unique=True,
        blank=False,
        help_text='Разрешены буквы, цифры и @/./+/-/_',
        error_messages={'unique': 'Пользователь уже существует!'},
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )

    @property
    def is_admin(self):
        return self.is_staff or self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class Category(CategoryAndGenre):
    """Категории."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryAndGenre):
    """Жанры."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Названия произведений."""

    name = models.CharField('Название', max_length=256)
    year = models.PositiveSmallIntegerField(
        'Год создания',
        validators=[MaxValueValidator(datetime.date.today().year,
                                      message='Год больше текущего')]
    )
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(Category,
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year',)
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:LENGTH_SHORT]


class Review(CommentsAndReviews):
    """Отзывы."""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(1, message='Минимальное значение 1'),
                    MaxValueValidator(10, message='Максимальное значение 10')
                    ]
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [models.UniqueConstraint(fields=['author', 'title'],
                                               name='unique_review')]
        default_related_name = 'reviews'


class Comment(models.Model):
    """Комментарии."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               verbose_name='Отзыв')
    text = models.TextField('Комментарий')
    pub_date = models.DateTimeField('Дата',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:LENGTH_SHORT]
