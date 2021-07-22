from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from .consumers import ChatConsumer
from .token_auth_channels import TokenAuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                [
                    url(r"^messages/(?P<chat_id>[\w.@+-]+)", ChatConsumer().as_asgi())
                ]
            )
        )
    )
})
