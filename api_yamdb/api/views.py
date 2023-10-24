from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from django.db.models import Avg
from reviews.models import Title


class TitleViewSet(viewsets.ModelViewSet):
    """Отображение действий с произведениями."""
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')


class ReviewViewSet(viewsets.ModelViewSet):
    """Отображение действий с отзывами."""

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)
