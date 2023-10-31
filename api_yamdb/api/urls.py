from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, Signup, TitleViewSet,
                       UserViewSet, get_token)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
# router_v1.register('auth/signup', SignupViewSet, basename='signup')
router_v1.register(r'titles/(?P<title_id>[1-9]\d*)/reviews',
                   ReviewViewSet,
                   basename='review')
router_v1.register(
    r'titles/(?P<title_id>[1-9]\d*)/reviews/(?P<review_id>[1-9]\d*)/comments',
    CommentViewSet,
    basename='comment')

urlpatterns = [
    path('v1/auth/token/', get_token),
    path('v1/auth/signup/', Signup.as_view(), name='signup'),
    path('v1/', include(router_v1.urls)),
]
