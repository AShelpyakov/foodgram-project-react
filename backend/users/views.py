from rest_framework.generics import ListAPIView

from .models import User
from .serializers import FollowListSerializer


class FollowListAPIView(ListAPIView):
    serializer_class = FollowListSerializer

    def get_queryset(self):
        return User.objects.filter(following__follower=self.request.user)
