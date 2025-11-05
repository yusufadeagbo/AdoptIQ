from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.core.web3_utils import generate_nonce, store_nonce, verify_nonce, verify_wallet_signature
from apps.core.authentication import create_jwt_token, create_refresh_token
from apps.users.models import User
import jwt
from django.conf import settings

class ChallengeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        wallet_address = request.data.get('wallet_address')
        if not wallet_address:
            return Response({'error': 'wallet_address is required'}, status=status.HTTP_400_BAD_REQUEST)

        nonce = generate_nonce()
        store_nonce(wallet_address, nonce)

        message = f"Sign this message to authenticate with AdoptIQ.\n\nNonce: {nonce}"

        return Response({
            'message': message,
            'nonce': nonce
        })

class VerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        wallet_address = request.data.get('wallet_address')
        signature = request.data.get('signature')
        nonce = request.data.get('nonce')

        if not all([wallet_address, signature, nonce]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        if not verify_nonce(wallet_address, nonce):
            return Response({'error': 'Invalid or expired nonce'}, status=status.HTTP_400_BAD_REQUEST)

        message = f"Sign this message to authenticate with AdoptIQ.\n\nNonce: {nonce}"
        if not verify_wallet_signature(wallet_address, signature, message):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            wallet_address=wallet_address.lower(),
            defaults={'display_name': f'User {wallet_address[:8]}'}
        )
        user.last_login_at = user.updated_at
        user.save()

        access_token = create_jwt_token(user)
        refresh_token = create_refresh_token(user)

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user.id),
                'wallet_address': user.wallet_address,
                'display_name': user.display_name,
                'email': user.email,
            }
        })

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'refresh_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            if payload.get('type') != 'refresh':
                return Response({'error': 'Invalid token type'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=payload['user_id'])
            access_token = create_jwt_token(user)

            return Response({'access_token': access_token})

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        return Response({'message': 'Logged out successfully'})
