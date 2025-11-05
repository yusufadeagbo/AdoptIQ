from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User, Project
from apps.missions.models import Mission, Participation

class MissionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            wallet_address='0x1234567890123456789012345678901234567890'
        )
        self.project = Project.objects.create(
            user=self.user,
            name='Test Project',
            category='nft'
        )

    def test_create_mission(self):
        mission = Mission.objects.create(
            project=self.project,
            name='Test Mission',
            description='Test Description',
            category='nft_mint',
            status='draft',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            target_participants=100,
            chain='ethereum'
        )
        self.assertEqual(mission.name, 'Test Mission')
        self.assertEqual(mission.status, 'draft')
        self.assertEqual(mission.current_participants, 0)

    def test_participation_creation(self):
        mission = Mission.objects.create(
            project=self.project,
            name='Test Mission',
            description='Test Description',
            category='nft_mint',
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            target_participants=100,
            chain='ethereum'
        )

        participation = Participation.objects.create(
            mission=mission,
            user=self.user,
            wallet_address=self.user.wallet_address,
            status='joined'
        )

        self.assertEqual(participation.status, 'joined')
        self.assertEqual(participation.mission, mission)
