from rest_framework import serializers

from users.models import User
from django.utils.translation import gettext_lazy as _


class UserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(min_length=8, max_length=4096)

    class Meta:
        model = User
        fields = ('password',
                  'password2',
                  'email',
                  'first_name',
                  'last_name',
                  'user_type',
                  'dob',
                  'school',
                  'school_year',
                  'school_email'
                  )

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError(_('Passwords are not equal!'))
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError(_('Email already in use!'))
        if attrs.get('user_type') == User.UserType.STUDENT:
            if not attrs.get('school_year'):
                raise serializers.ValidationError(_('Please specify your school year.'))
        return attrs
