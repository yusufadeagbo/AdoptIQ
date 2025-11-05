from django.test import TestCase
from apps.users.models import User, Project

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create(
            wallet_address='0x1234567890123456789012345678901234567890',
            display_name='Test User'
        )
        self.assertEqual(user.wallet_address, '0x1234567890123456789012345678901234567890')
        self.assertEqual(user.display_name, 'Test User')

    def test_wallet_address_uniqueness(self):
        User.objects.create(wallet_address='0x1234567890123456789012345678901234567890')
        with self.assertRaises(Exception):
            User.objects.create(wallet_address='0x1234567890123456789012345678901234567890')

class ProjectModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            wallet_address='0x1234567890123456789012345678901234567890'
        )

    def test_create_project(self):
        project = Project.objects.create(
            user=self.user,
            name='Test Project',
            description='Test Description',
            category='nft'
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.category, 'nft')
        self.assertEqual(project.user, self.user)
