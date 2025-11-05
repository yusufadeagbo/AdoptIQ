from django.db import models
from apps.users.models import Project
import uuid

class Subscription(models.Model):
    PLAN_TIER_CHOICES = [
        ('starter', 'Starter'),
        ('growth', 'Growth'),
        ('enterprise', 'Enterprise'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('canceled', 'Canceled'),
        ('grace_period', 'Grace Period'),
    ]

    PAYMENT_TOKEN_CHOICES = [
        ('USDC', 'USDC'),
        ('USDT', 'USDT'),
        ('DAI', 'DAI'),
        ('ETH', 'ETH'),
        ('MATIC', 'MATIC'),
    ]

    CHAIN_CHOICES = [
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='subscription')
    plan_tier = models.CharField(max_length=20, choices=PLAN_TIER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    payment_token = models.CharField(max_length=10, choices=PAYMENT_TOKEN_CHOICES, default='USDC')
    payment_chain = models.CharField(max_length=20, choices=CHAIN_CHOICES, default='ethereum')
    wallet_address = models.CharField(max_length=42)
    amount_per_cycle = models.DecimalField(max_digits=18, decimal_places=6)
    billing_cycle_days = models.IntegerField(default=30)
    next_billing_date = models.DateTimeField()
    allowance_set = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.plan_tier}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=18, decimal_places=6)
    token = models.CharField(max_length=10)
    chain = models.CharField(max_length=20)
    transaction_hash = models.CharField(max_length=66, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    billing_date = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-billing_date']
        indexes = [
            models.Index(fields=['subscription']),
            models.Index(fields=['billing_date', 'status']),
            models.Index(fields=['transaction_hash']),
        ]

    def __str__(self):
        return f"{self.subscription.project.name} - {self.amount} {self.token}"

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    invoice_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=6)
    due_date = models.DateTimeField()
    paid_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_number}"
