from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Review, Comments


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
