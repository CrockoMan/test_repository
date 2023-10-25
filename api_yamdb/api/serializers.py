from datetime import datetime as dt

from rest_framework import serializers

from reviews.models import (Review, Comments, Title,
                            Category, Genre, User)


# class ReviewSerializer(serializers.ModelSerializer):
#     """Отзывы."""
#     author = serializers.SlugRelatedField(
#         read_only=True, slug_field='username'
#     )
#
#     class Meta:
#         fields = '__all__'
#         model = Review
#         read_only_fields = ('author', 'title')
class ReviewSerializer(serializers.ModelSerializer):
    """Отзывы."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('author', 'title' )
        # validators = [
        #     UniqueTogetherValidator(queryset=Review.objects.all(),
        #                             fields=('author', 'title'))
        # ]

    def validate(self, value):
        request = self.context.get('request')
        author = request.user

        if Review.objects.filter(
                author=author,
                title=self.context['view'].kwargs['title_id']).exists():
            raise serializers.ValidationError('Not applied many review')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Отзывы."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comments
        read_only_fields = ('author', 'review' )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с жанрами."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для работы с категориями."""
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о произведениях."""

    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения инфо о произведениях."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def validate_year(self, data):
        if data >= dt.now().year:
            raise serializers.ValidationError(
                f'Год {data} больше текущего!',
            )
        return data
