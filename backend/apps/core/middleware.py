from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from apps.core.authentication import JWTAuthentication

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])

        if b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Bearer':
                    scope['user'] = await self.get_user(token_key)
                else:
                    scope['user'] = AnonymousUser()
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            query_string = scope.get('query_string', b'').decode()
            params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = params.get('token')

            if token:
                scope['user'] = await self.get_user(token)
            else:
                scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token):
        from django.http import HttpRequest
        request = HttpRequest()
        request.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        request.headers = {'Authorization': f'Bearer {token}'}

        auth = JWTAuthentication()
        try:
            user, _ = auth.authenticate(request)
            return user
        except Exception:
            return AnonymousUser()
