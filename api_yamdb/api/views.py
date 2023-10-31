from http import HTTPStatus

from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, views, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import FilterForTitle
from api.permissions import (IsAdminOnlyPermission, IsAdminOrReadOnly,
                             IsAuthorModeratorAdminOrReadOnlyPermission)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignupSerializer, TitleReadSerializer,
                             TitleWriteSerializer, TokenUserSerializer,
                             UserSerializer)
from api_yamdb.settings import EMAIL_SENDER
from reviews.models import Category, Genre, Review, Title, User

NO_PUT_METHODS = ('get', 'post', 'patch', 'delete', 'head', 'options', 'trace')


class TitleViewSet(viewsets.ModelViewSet):
    """Отображение действий с произведениями."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-year')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = FilterForTitle
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
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Отображение действий с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnlyPermission, )
    http_method_names = NO_PUT_METHODS
    pagination_class = LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(Review,
                                 title=self.kwargs['title_id'],
                                 pk=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


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
            permission_classes=(IsAuthenticated,))
    def me_path_user(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = UserSerializer(user,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=self.request.user.role)
        return Response(serializer.data, status=HTTPStatus.OK)


# class SignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     """Регистрация."""
#
#     queryset = User.objects.all()
#     permission_classes = (permissions.AllowAny,)
#     serializer_class = SignupSerializer
#
#     def create(self, request):
#         serializer = SignupSerializer(data=request.data)
#         if (User.objects.filter(username=request.data.get('username'),
#                                 email=request.data.get('email'))):
#             user = User.objects.get(username=request.data.get('username'))
#             serializer = SignupSerializer(user, data=request.data)
#         if serializer.is_valid():
#             serializer.save(
#                 confirmation_code=User.objects.make_random_password(length=20)
#             )
#             username = request.data.get('username')
#             user = User.objects.get(username=username)
#             send_mail('Код подтверждения',
#                       f'Ваш код подтверждения: {user.confirmation_code}',
#                       EMAIL_SENDER,
#                       [user.email],
#                       fail_silently=False)
#             return Response(serializer.data, status=HTTPStatus.OK)
#         return Response(serializer.errors, status=400)
class Signup(views.APIView):
    """Функция регистрации новых пользователей."""

    serializer_class = SignupSerializer
    permission_classes = AllowAny,

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(
                username=serializer.validated_data.get('username'),
                email=serializer.validated_data.get('email'),
                confirmation_code=User.objects.make_random_password(length=20)
            )
        except IntegrityError:
            return Response('Этот username недоступен', HTTP_400_BAD_REQUEST)
        # code = User.objects.make_random_password(length=20)
        send_mail('Код подтверждения',
                  f'Ваш код подтверждения: {user.confirmation_code}',
                  EMAIL_SENDER,
                  [user.email],
                  fail_silently=False)
        return Response(serializer.data, status=HTTPStatus.OK)
        # send_mail(
        #     'Код токена',
        #     f'Код для получения токена {code}',
        #     settings.DEFAULT_FROM_EMAIL,
        #     [serializer.validated_data.get('email')]
        # )
        # return response.Response(
        #     serializer.data, status=status.HTTP_200_OK


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Получение токена."""

    serializer = TokenUserSerializer(data=request.data)
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=username)
    if user.confirmation_code == confirmation_code:
        token = RefreshToken.for_user(user)
        return Response({'token': str(token.access_token)},
                        status=HTTPStatus.OK)

    return Response('Error', status=400)
