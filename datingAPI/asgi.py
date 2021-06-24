import os

from django.core.asgi import get_asgi_application
import myapp.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from myapp.token_auth_channels import TokenAuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datingAPI.settings")


application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            myapp.routing.websocket_urlpatterns
        )
  ),
})
