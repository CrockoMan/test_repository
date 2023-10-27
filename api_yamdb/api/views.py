from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from django.db.models import Avg
from rest_framework.pagination import LimitOffsetPagination

from api.serializers import ReviewSerializer, CommentSerializer
from reviews.models import Title, Comments, Review


class TitleViewSet(viewsets.ModelViewSet):
    """Отображение действий с произведениями."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')


class ReviewViewSet(viewsets.ModelViewSet):
    """Отображение действий с отзывами."""

    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Отображение действий с комментариями."""
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def ger_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        # title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        review = self.ger_review()
        return review.comments.all()

    def perform_create(self, serializer):
        # title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        review = self.ger_review()
        serializer.save(author=self.request.user, review=review)
