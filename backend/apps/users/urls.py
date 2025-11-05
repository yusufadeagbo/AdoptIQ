from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')
router.register(r'projects', ProjectViewSet, basename='projects')

urlpatterns = [
    path('', include(router.urls)),
]
