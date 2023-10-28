import random

from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from rest_framework import mixins, permissions
from django.db.models import Avg
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Title, Category, Genre, Review, User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .filters import FilterForTitle
from .permissions import (IsAdminOrReadOnly,
                          IsAdminOnlyPermission,
                          IsAuthorModeratorAdminOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnlyPermission,
                          OnlySelfUserPermission)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          ReviewSerializer, CommentSerializer, UserSerializer,
                          UserMePathSerializer, SignupSerializer,
                          TokenUserSerializer)

NO_PUT_METHODS = ('get', 'post', 'patch', 'delete', 'head', 'options', 'trace')


class TitleViewSet(viewsets.ModelViewSet):
    """Отображение действий с произведениями."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, )
    filterset_class = FilterForTitle
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
    pagination_class = LimitOffsetPagination
    http_method_names = NO_PUT_METHODS

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Отображение действий с жанрами для произведений."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Отображение действий с категориями произведений."""
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = LimitOffsetPagination


class ReviewViewSet(viewsets.ModelViewSet):
    """Отображение действий с отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnlyPermission, )
    http_method_names = NO_PUT_METHODS
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs['title_id'])

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user,
                        title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Отображение действий с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly, )
    # http_method_names = ['get', 'post', 'patch']
    http_method_names = NO_PUT_METHODS
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review,
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
    permission_classes = (IsAdminOnlyPermission,)
    http_method_names = NO_PUT_METHODS

    @action(methods=['get', 'patch'], url_path='me', detail=False,
            permission_classes=(OnlySelfUserPermission,))
    def me_path_user(self, request):
        user = User.objects.get(username=request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = UserMePathSerializer(user,
                                          data=request.data,
                                          partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class SignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SignupSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = SignupSerializer(data=request.data)
        if (User.objects.filter(username=request.data.get('username'),
                                email=request.data.get('email'))):
            user = User.objects.get(username=request.data.get('username'))
            serializer = SignupSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save(
                confirmation_code=User.objects.make_random_password(length=20)
            )
            username = request.data.get('username')
            user = User.objects.get(username=username)
            send_mail('Код подтверждения',
                      f'Ваш код подтверждения: {user.confirmation_code}',
                      'noreply@example.com',
                      [user.email],
                      fail_silently=False)
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Получение токена."""

    serializer = TokenUserSerializer(data=request.data)
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    if serializer.is_valid():
        user = get_object_or_404(User, username=username)
        if user.confirmation_code == confirmation_code:
            token = RefreshToken.for_user(user)
            return Response({'token': str(token.access_token)}, status=200)

    return Response('Error', status=400)
