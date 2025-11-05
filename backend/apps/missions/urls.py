from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.missions.views import MissionViewSet, ParticipationViewSet

router = DefaultRouter()
router.register(r'', MissionViewSet, basename='missions')
router.register(r'participations', ParticipationViewSet, basename='participations')

urlpatterns = [
    path('', include(router.urls)),
]
