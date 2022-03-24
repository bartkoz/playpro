from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import EmailUniquenessAPIView, UserCreateAPIView, SchoolListAPIView

urlpatterns = [
    path('email-uniqueness/<str:email>/', EmailUniquenessAPIView.as_view()),
    path('schools/', SchoolListAPIView.as_view()),
    path('create/', UserCreateAPIView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]
