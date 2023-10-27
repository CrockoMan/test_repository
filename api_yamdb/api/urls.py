from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TitleViewSet, ReviewViewSet, CommentViewSet

router_v1 = DefaultRouter()

router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet,
                   basename='reviews')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/('
                   r'?P<review_id>\d+)/comments',
                   CommentViewSet,
                   basename='comments')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    # path('v1/', include('djoser.urls.jwt')),
]
