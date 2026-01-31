import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import home.routing
import project_ms.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_CRM.settings')

# from channels.auth import AuthMiddlewareStack
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             home.routing.websocket_urlpatterns +    
#             project_ms.routing.websocket_urlpatterns
#         )
#     ),
# })


from home.middlewares import TokenAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(
            home.routing.websocket_urlpatterns +
            project_ms.routing.websocket_urlpatterns
        )
    ),
})
