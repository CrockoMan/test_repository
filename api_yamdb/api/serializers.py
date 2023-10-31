from datetime import datetime as dt

from django.db.models import Avg
from rest_framework import serializers

from api.utils import check_for_me_name
from reviews.models import Category, Comment, Genre, Review, Title, User


class ReviewSerializer(serializers.ModelSerializer):
    """Работа с отзывами."""

    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, value):
        if self.context['request'].method in ['POST']:
            if Review.objects.filter(author=self.context.get('request').user,
                                     title=self.context['view'].kwargs[
                                         'title_id']).exists():
                raise serializers.ValidationError('Not applied many review')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Работа с комментариями."""
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    """Работа с жанрами."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Работа с категориями."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Получение информации о произведениях."""

    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Добавление и изменение информации о произведениях."""

    genre = serializers.SlugRelatedField(slug_field='slug',
                                         many=True,
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')

    def validate_year(self, data):
        if data >= dt.now().year:
            raise serializers.ValidationError(f'Wrond data {data}')
        return data

    def to_representation(self, value):
        return TitleReadSerializer(value).data


class UserSerializer(serializers.ModelSerializer):
    """Работа с пользователями"""

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Имя me запрещено')
        return value


class SignupSerializer(serializers.ModelSerializer):
    """Регистрация или обновление пользователя"""

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        check_for_me_name(value)
        return value


class TokenUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
