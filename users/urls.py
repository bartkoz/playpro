from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import (
    EmailUniquenessAPIView,
    UserCreateAPIView,
    SchoolListAPIView,
    UserPasswordResetLinkGenerateAPIView,
    UserPasswordResetAPIView,
    AvailableAvatarsAPIView,
    ProfileAPIView,
    UserTeamsAPIView,
)

app_name = "users"

urlpatterns = [
    path("email-uniqueness/<str:email>/", EmailUniquenessAPIView.as_view()),
    path("schools/", SchoolListAPIView.as_view()),
    path("create/", UserCreateAPIView.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password-reset/", UserPasswordResetLinkGenerateAPIView.as_view()),
    path(
        "password-reset/<str:uidb64>/<str:token>/", UserPasswordResetAPIView.as_view()
    ),
    path("available-avatars/", AvailableAvatarsAPIView.as_view()),
    path("profile/", ProfileAPIView.as_view()),
    path("user-teams/", UserTeamsAPIView.as_view()),
]
