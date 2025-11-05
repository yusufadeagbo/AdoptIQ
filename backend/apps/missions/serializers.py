from rest_framework import serializers
from apps.missions.models import Mission, Participation, MissionVerificationLog
from apps.users.serializers import ProjectSerializer

class MissionSerializer(serializers.ModelSerializer):
    project_details = ProjectSerializer(source='project', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = ['id', 'project', 'project_details', 'name', 'description', 'category', 'status',
                  'start_date', 'end_date', 'target_participants', 'current_participants',
                  'criteria', 'reward_config', 'chain', 'created_at', 'updated_at',
                  'completed_at', 'progress_percentage']
        read_only_fields = ['id', 'current_participants', 'created_at', 'updated_at', 'completed_at']

    def get_progress_percentage(self, obj):
        if obj.target_participants > 0:
            return round((obj.current_participants / obj.target_participants) * 100, 2)
        return 0

class ParticipationSerializer(serializers.ModelSerializer):
    mission_details = MissionSerializer(source='mission', read_only=True)

    class Meta:
        model = Participation
        fields = ['id', 'mission', 'mission_details', 'user', 'wallet_address', 'status',
                  'transaction_hash', 'verification_attempts', 'verified_at', 'rejection_reason',
                  'reward_distributed', 'fraud_score', 'metadata', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'wallet_address', 'status', 'verification_attempts',
                            'verified_at', 'fraud_score', 'created_at', 'updated_at']

class MissionVerificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionVerificationLog
        fields = ['id', 'participation', 'status', 'details', 'checked_at']
        read_only_fields = ['id', 'checked_at']
