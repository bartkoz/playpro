from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import User, School
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
        errors = []
        if attrs.get('password') != attrs.get('password2'):
            errors.append({'password': _('Passwords are not equal!')})
        if User.objects.filter(email=attrs.get('email')).exists():
            errors.append({'email': _('Email already in use!')})
        if attrs.get('user_type') == User.UserType.STUDENT:
            if not attrs.get('school_year'):
                errors.append({'school_year': _('Please specify your school year.')})
        password_validators = get_default_password_validators()
        for validator in password_validators:
            try:
                validator.validate(attrs.get('password'))
            except ValidationError as error:
                errors.append({'password': error})
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = ('name', 'id')
