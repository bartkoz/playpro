from datetime import datetime

import pytz
from coreapi.compat import force_text
from django.contrib.auth import get_user
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext as _
from django.conf import settings
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from tournaments.models import TournamentTeam
from tournaments.serializers import TournamentMatchContestantsSerializer
from users.models import User, School, UserAvatar
from users.serializers import (
    UserCreateSerializer,
    EmailResetSerializer,
    EmailPasswordChangedSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    ProfilePasswordUpdateSerializer,
    SchoolSerializer,
    AvatarSerializer,
)

from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class EmailUniquenessAPIView(APIView):
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        return Response(
            {"is_unique": not User.objects.filter(email=kwargs.get("email")).exists()}
        )


class UserCreateAPIView(APIView):

    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                User.objects.get(email=data.get("email"))
                return Response(
                    {"errors": "User with such email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except User.DoesNotExist:
                data.pop("tos_accepted")
                user = User(**data)
                user.set_password(data.get("password"))
                # user.is_active = False
                user.save()
                return Response(
                    {"token": get_tokens_for_user(user)}, status=status.HTTP_200_OK
                )
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class UserPasswordResetLinkGenerateAPIView(APIView):
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = EmailResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data.get("email"))
            if user.resend_activation_mail_available:
                mail_subject = _("Password reset - Playpro.gg")
                message = render_to_string(
                    "users/acc_password_reset_mail.html",
                    {
                        "user": user,
                        "domain": getattr(settings, "PLAYPRO_URL"),
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": PasswordResetTokenGenerator().make_token(user),
                    },
                )
                email = EmailMessage(
                    mail_subject,
                    message,
                    to=[
                        user.email,
                    ],
                )
                email.content_subtype = "html"
                email.send()
                user.last_email_reset = datetime.utcnow().replace(tzinfo=pytz.UTC)
                user.save()
            else:
                return Response(
                    {
                        "error": _(
                            "You may obtain password reset email once every {} minutes"
                        ).format(getattr(settings, "EMAIL_RESEND_DELAY"))
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            pass
        return Response(
            {
                "success": _(
                    "Please confirm password reset by clicking a link sent to your email."
                )
            }
        )


class UserPasswordResetAPIView(APIView):
    permission_classes = ()
    token_generator = PasswordResetTokenGenerator

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            user = None
        return user

    def _get_user_or_return_error(self, uidb64):
        uid = urlsafe_base64_decode(uidb64).decode("utf-8")
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"Email not found."}, status=status.HTTP_400_BAD_REQUEST)
        return user

    def get(self, request, *args, **kwargs):
        user = self._get_user_or_return_error(kwargs["uidb64"])
        token_correct = self.token_generator().check_token(user, kwargs["token"])
        if not user or not token_correct:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = self._get_user_or_return_error(kwargs["uidb64"])
        token_correct = self.token_generator().check_token(user, kwargs["token"])

        if user and token_correct:
            serializer = EmailPasswordChangedSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data["password"])
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class ProfileAPIView(RetrieveUpdateAPIView):
    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProfileSerializer
        elif any(
            [
                x in self.request.data.keys()
                for x in ["current_password", "new_password"]
            ]
        ):
            return ProfilePasswordUpdateSerializer
        return ProfileUpdateSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, *args, **kwargs)
        serializer.is_valid(raise_exception=True)
        if isinstance(serializer, ProfilePasswordUpdateSerializer):
            instance.set_password(serializer.validated_data["new_password"])
        else:
            for k, v in serializer.validated_data.items():
                setattr(instance, k, v)
        instance.save()
        return Response(ProfileSerializer(instance).data, status=status.HTTP_200_OK)


class SchoolListAPIView(ListAPIView):
    permission_classes = ()
    serializer_class = SchoolSerializer
    queryset = School.objects.all()


class AvailableAvatarsAPIView(ListAPIView):

    serializer_class = AvatarSerializer
    queryset = UserAvatar.objects.all()


class UserTeamsAPIView(ListAPIView):

    serializer_class = TournamentMatchContestantsSerializer

    def get_queryset(self):
        return TournamentTeam.objects.filter(team_members__user=self.request.user)
