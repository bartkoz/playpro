import os
import django
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

import urls

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "playpro.settings")

django.setup()

application = ProtocolTypeRouter(
    {
        "http": AsgiHandler(),
        "websocket": AuthMiddlewareStack(URLRouter(urls.websocket_urlpatterns)),
    }
)
