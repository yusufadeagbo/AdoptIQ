from rest_framework import serializers
from apps.users.models import User, Project, Achievement

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'wallet_address', 'email', 'display_name', 'created_at', 'last_login_at', 'preferences']
        read_only_fields = ['id', 'wallet_address', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'user', 'name', 'description', 'website_url', 'twitter_handle',
                  'discord_url', 'category', 'logo_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'user', 'achievement_type', 'title', 'description', 'earned_at', 'metadata']
        read_only_fields = ['id', 'user', 'earned_at']
