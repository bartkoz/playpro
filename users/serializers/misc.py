from rest_framework import serializers

from users.models import School, UserAvatar


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ("name", "id")


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("image",)
        model = UserAvatar
