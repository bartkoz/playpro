from django.contrib.auth.password_validation import (
    get_default_password_validators,
)
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import User
from django.utils.translation import gettext_lazy as _


class UserCreateSerializer(serializers.ModelSerializer):
    tos_accepted = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "password",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "dob",
            "school",
            "school_year",
            "school_email",
            "tos_accepted"
        )

    def validate(self, attrs):
        errors = []
        if not attrs.get("tos_accepted"):
            errors.append({"tos_accepted": _("You need to accept terms of service.")})
        if User.objects.filter(email=attrs.get("email")).exists():
            errors.append({"email": _("Email already in use!")})
        if attrs.get("user_type") == User.UserType.STUDENT:
            if not attrs.get("school_year"):
                errors.append({"school_year": _("Please specify your school year.")})
        password_validators = get_default_password_validators()
        for validator in password_validators:
            try:
                validator.validate(attrs.get("password"))
            except ValidationError as error:
                errors.append({"password": error})
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class EmailResetSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)


class EmailPasswordChangedSerializer(serializers.Serializer):

    password = serializers.CharField(required=True)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "nickname",
            "first_name",
            "last_name",
            "avatar",
            "epic_games_id",
            "ea_games_id",
            "ps_network_id",
            "riot_id",
        )
        model = User


class ProfileSerializer(serializers.ModelSerializer):

    avatar = serializers.URLField(source="avatar.image.url")
    school_name = serializers.CharField(source="school.name")

    class Meta:
        fields = (
            "avatar",
            "email",
            "first_name",
            "last_name",
            "dob",
            "school_email",
            "school_name",
            "school_year",
            "epic_games_id",
            "ea_games_id",
            "ps_network_id",
            "riot_id",
        )
        model = User


class ProfilePasswordUpdateSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password("value"):
            return serializers.ValidationError(_("Current password does not match"))
        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        user.set_password(value)
        user.save()
        return value
