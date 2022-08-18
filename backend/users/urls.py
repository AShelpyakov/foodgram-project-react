from django.urls import include, path

from .views import FollowAPIView, FollowListAPIView

urlpatterns = [
    path(
        'users/<int:id>/subscribe/',
        FollowAPIView.as_view(),
        name='subscribe',
    ),
    path(
        'users/subscriptions/',
        FollowListAPIView.as_view(),
        name='subscriptions',
    ),
    path('', include('djoser.urls')),
]
