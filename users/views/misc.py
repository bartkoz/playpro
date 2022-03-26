from rest_framework.generics import ListAPIView

from users.models import School
from users.serializers import SchoolSerializer


class SchoolListAPIView(ListAPIView):
    permission_classes = ()
    serializer_class = SchoolSerializer
    queryset = School.objects.all()
