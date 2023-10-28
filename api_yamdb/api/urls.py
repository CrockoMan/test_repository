from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (TitleViewSet, CategoryViewSet,
                       GenreViewSet, ReviewViewSet,
                       CommentViewSet, UserViewSet, SignupViewSet,
                       get_token)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'auth/signup', SignupViewSet, basename='signup')
router_v1.register(r'titles/(?P<title_id>[1-9]\d*)/reviews',
                   ReviewViewSet,
                   basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>[1-9]\d*)/reviews/(?P<review_id>[1-9]\d*)/comments',
    CommentViewSet,
    basename='comments')


urlpatterns = [
    path('v1/auth/token/', get_token),

    path('v1/', include(router_v1.urls)),
]
