from django.urls import path
from apps.core.views import ChallengeView, VerifyView, RefreshTokenView, LogoutView

urlpatterns = [
    path('challenge/', ChallengeView.as_view(), name='auth-challenge'),
    path('verify/', VerifyView.as_view(), name='auth-verify'),
    path('refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
]
