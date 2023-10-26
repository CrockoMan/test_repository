from rest_framework import viewsets
from django.db.models import Avg
from reviews.models import Title, Category, Genre, Review
from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .filters import FilterForTitle
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          ReviewSerializer, CommentSerializer)


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

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title=self.kwargs['title_id'],
            pk=self.kwargs['review_id'])
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    """Работа с профилем пользователя."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(methods=['get', 'patch'], url_path='me', detail=False)
    def me_path_user(self, request):
        user = User.objects.get(username=request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = UserSerializer(user, ata=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
