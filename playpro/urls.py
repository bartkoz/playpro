from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from playpro import sockets

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("users/", include("users.urls")),
    path("tournaments/", include("tournaments.urls")),
    path('sentry-debug/', trigger_error),
]

websocket_urlpatterns = [
    path("notifications/<str:name>/", sockets.NotificationConsumer.as_asgi()),
    path("match-lobby/<str:name>/", sockets.PreMatchChatConsumer.as_asgi()),
]
