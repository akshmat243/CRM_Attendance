# vrindavan_crm/asgi.py

import os
from channels.routing import get_default_application
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import home.routing
import project_ms.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_CRM.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            home.routing.websocket_urlpatterns,
            project_ms.routing.websocket_urlpatterns
        )
    ),
})
