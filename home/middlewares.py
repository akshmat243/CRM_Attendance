from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user_from_token(token_key):
    # ✅ IMPORTS INSIDE FUNCTION (IMPORTANT)
    from django.contrib.auth.models import AnonymousUser
    from rest_framework.authtoken.models import Token

    try:
        token = Token.objects.select_related("user").get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Default user
        scope["user"] = None

        query = parse_qs(scope["query_string"].decode())
        token = query.get("token")

        if token:
            scope["user"] = await get_user_from_token(token[0])

        return await super().__call__(scope, receive, send)
