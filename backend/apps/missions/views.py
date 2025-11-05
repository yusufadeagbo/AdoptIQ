from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from apps.missions.models import Mission, Participation
from apps.missions.serializers import MissionSerializer, ParticipationSerializer
from apps.missions.tasks import verify_participation
from apps.core.pagination import StandardResultsSetPagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Mission.objects.all()

        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset

    def perform_create(self, serializer):
        mission = serializer.save()
        if mission.start_date <= timezone.now() <= mission.end_date:
            mission.status = 'active'
            mission.save()

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        mission = self.get_object()
        if mission.status != 'draft':
            return Response({'error': 'Mission is not in draft status'}, status=status.HTTP_400_BAD_REQUEST)

        mission.status = 'active'
        mission.save()

        return Response(MissionSerializer(mission).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        mission = self.get_object()
        if mission.status != 'active':
            return Response({'error': 'Mission is not active'}, status=status.HTTP_400_BAD_REQUEST)

        mission.status = 'paused'
        mission.save()

        return Response(MissionSerializer(mission).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        mission = self.get_object()
        mission.status = 'completed'
        mission.completed_at = timezone.now()
        mission.save()

        return Response(MissionSerializer(mission).data)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        mission = self.get_object()
        participations = Participation.objects.filter(mission=mission)

        status_filter = request.query_params.get('status')
        if status_filter:
            participations = participations.filter(status=status_filter)

        serializer = ParticipationSerializer(participations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        mission = self.get_object()

        analytics = {
            'total_participants': mission.current_participants,
            'target_participants': mission.target_participants,
            'progress_percentage': (mission.current_participants / mission.target_participants * 100) if mission.target_participants > 0 else 0,
            'verified_count': Participation.objects.filter(mission=mission, status='verified').count(),
            'pending_count': Participation.objects.filter(mission=mission, status='pending').count(),
            'rejected_count': Participation.objects.filter(mission=mission, status='rejected').count(),
            'days_remaining': (mission.end_date - timezone.now()).days if mission.end_date > timezone.now() else 0,
        }

        return Response(analytics)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        mission = self.get_object()
        user = request.user

        if mission.status != 'active':
            return Response({'error': 'Mission is not active'}, status=status.HTTP_400_BAD_REQUEST)

        participation, created = Participation.objects.get_or_create(
            mission=mission,
            user=user,
            wallet_address=user.wallet_address,
            defaults={'status': 'joined'}
        )

        if not created:
            return Response({'error': 'Already joined this mission'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ParticipationSerializer(participation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def submit_action(self, request, pk=None):
        mission = self.get_object()
        user = request.user
        transaction_hash = request.data.get('transaction_hash')

        if not transaction_hash:
            return Response({'error': 'transaction_hash is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participation = Participation.objects.get(mission=mission, user=user)
        except Participation.DoesNotExist:
            return Response({'error': 'Must join mission first'}, status=status.HTTP_400_BAD_REQUEST)

        participation.transaction_hash = transaction_hash
        participation.status = 'pending'
        participation.save()

        verify_participation.delay(str(participation.id))

        return Response({'message': 'Verification queued', 'participation_id': str(participation.id)})

class ParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Participation.objects.filter(user=self.request.user)
        return Participation.objects.none()
