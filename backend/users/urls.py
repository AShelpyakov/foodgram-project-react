from django.urls import include, path

from .views import FollowListAPIView

urlpatterns = [
    path(
        'users/subscriptions/',
        FollowListAPIView.as_view(),
        name='subscription'
    ),
    path('', include('djoser.urls')),
]
