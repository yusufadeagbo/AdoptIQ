from django.db import models
from apps.users.models import User, Project
import uuid

class Mission(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    CATEGORY_CHOICES = [
        ('nft_mint', 'NFT Minting'),
        ('token_liquidity', 'Token Liquidity'),
        ('staking', 'Staking'),
        ('trading_volume', 'Trading Volume'),
        ('governance', 'Governance'),
        ('social_hybrid', 'Social + On-Chain'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='missions')
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    target_participants = models.IntegerField()
    current_participants = models.IntegerField(default=0)
    criteria = models.JSONField(default=dict)
    reward_config = models.JSONField(default=dict)
    chain = models.CharField(max_length=50, default='ethereum')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'missions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class Participation(models.Model):
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    wallet_address = models.CharField(max_length=42, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='joined', db_index=True)
    transaction_hash = models.CharField(max_length=66, null=True, blank=True)
    verification_attempts = models.IntegerField(default=0)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    reward_distributed = models.BooleanField(default=False)
    fraud_score = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'participations'
        ordering = ['-created_at']
        unique_together = ['mission', 'wallet_address']
        indexes = [
            models.Index(fields=['mission', 'status']),
            models.Index(fields=['wallet_address', 'mission']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.mission.name} - {self.wallet_address}"

class MissionVerificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='verification_logs')
    status = models.CharField(max_length=20)
    details = models.JSONField(default=dict)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mission_verification_logs'
        ordering = ['-checked_at']

class BlockchainEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chain = models.CharField(max_length=50, db_index=True)
    block_number = models.BigIntegerField(db_index=True)
    transaction_hash = models.CharField(max_length=66, db_index=True)
    contract_address = models.CharField(max_length=42, db_index=True)
    event_name = models.CharField(max_length=255)
    event_data = models.JSONField(default=dict)
    processed = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blockchain_events'
        ordering = ['-block_number']
        indexes = [
            models.Index(fields=['chain', 'processed']),
            models.Index(fields=['contract_address', 'event_name']),
        ]
