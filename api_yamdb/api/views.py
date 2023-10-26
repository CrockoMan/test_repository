from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .filters import FilterForTitle
from .serializers import (CategorySerializer,
                          GenreSerializer, ReviewSerializer, CommentSerializer,
                          TitleReadSerializer, TitleWriteSerializer)
from reviews.models import User, Title, Category, Genre, Review
from .permissions import (IsAdminOrReadOnly,
                          IsAuthorOrModeratorOrAdminOrReadOnly)


class TitleViewSet(viewsets.ModelViewSet):
    """Отображение действий с произведениями."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, )
    filterset_class = FilterForTitle
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class GenreViewSet(viewsets.ModelViewSet):
    """Отображение действий с жанрами для произведений."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class CategoryViewSet(viewsets.ModelViewSet):
    """Отображение действий с категориями произведений."""
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    """Отображение действий с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorOrModeratorOrAdminOrReadOnly,
    )

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
    permission_classes = (
        IsAuthorOrModeratorOrAdminOrReadOnly,
    )

    def ger_review(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def get_queryset(self):
        review = get_object_or_404(Title, pk=self.kwargs['title_id'])
        review = self.ger_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Title, pk=self.kwargs['title_id'])
        review = self.ger_review()
        serializer.save(author=self.request.user, review=review)
