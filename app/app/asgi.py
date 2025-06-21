import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Delayed import inside function
def get_websocket_application():
    from chat.routing import websocket_urlpatterns
    return AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    )

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        get_websocket_application()
    ),
})