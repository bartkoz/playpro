from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserCreateSerializer


class EmailUniquenessAPIView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({"is_unique": not User.objects.filter(email=kwargs.get("email")).exists()})


class UserCreateAPIView(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                User.objects.get(email=data.get('email'))
                return Response(
                    {'errors': 'User with such email already exists.'}, status=status.HTTP_400_BAD_REQUEST
                )
            except User.DoesNotExist:
                data.pop('password2')
                user = User(**data)
                user.set_password(data.get('password'))
                # user.is_active = False
                user.save()
                return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
