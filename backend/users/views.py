from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from .models import Follow, User
from .serializers import FollowListSerializer, FollowSerializer


class FollowListAPIView(ListAPIView):
    serializer_class = FollowListSerializer

    def get_queryset(self):
        return User.objects.filter(following__follower=self.request.user)


class FollowAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = {'follower': request.user.id, 'following': kwargs.get('id')}
        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        following = get_object_or_404(User, id=kwargs.get('id'))
        follow = get_object_or_404(
            Follow, follower=request.user, following=following
        )
        follow.delete()
        return Response(status=HTTP_204_NO_CONTENT)
