from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.models import User, Project, Achievement
from apps.users.serializers import UserSerializer, ProjectSerializer, AchievementSerializer
from apps.core.pagination import StandardResultsSetPagination

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        from apps.missions.models import Participation
        from apps.billing.models import Subscription

        stats = {
            'total_participations': Participation.objects.filter(user=user).count(),
            'verified_participations': Participation.objects.filter(user=user, status='verified').count(),
            'total_projects': Project.objects.filter(user=user).count(),
            'active_subscriptions': Subscription.objects.filter(project__user=user, status='active').count(),
            'achievements_count': Achievement.objects.filter(user=user).count(),
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def achievements(self, request):
        achievements = Achievement.objects.filter(user=request.user)
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Project.objects.filter(user=self.request.user)
        return Project.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
