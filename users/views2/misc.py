from rest_framework.generics import ListAPIView

from users.models import School, UserAvatar
from users.serializers import SchoolSerializer, AvatarSerializer


class SchoolListAPIView(ListAPIView):
    permission_classes = ()
    serializer_class = SchoolSerializer
    queryset = School.objects.all()


class AvailableAvatarsAPIView(ListAPIView):

    serializer_class = AvatarSerializer
    queryset = UserAvatar.objects.all()
