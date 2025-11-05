from django.db import models
from apps.users.models import Project
import uuid

class Audit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('analyzing', 'Analyzing'),
        ('generating', 'Generating Report'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='audits')
    contract_address = models.CharField(max_length=42, db_index=True)
    contract_chain = models.CharField(max_length=50, default='ethereum')
    source_code = models.TextField(null=True, blank=True)
    compiler_version = models.CharField(max_length=100, null=True, blank=True)
    complexity_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    findings_count = models.IntegerField(default=0)
    critical_count = models.IntegerField(default=0)
    high_count = models.IntegerField(default=0)
    medium_count = models.IntegerField(default=0)
    low_count = models.IntegerField(default=0)
    overall_risk = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, null=True, blank=True)
    report_ipfs_hash = models.CharField(max_length=255, null=True, blank=True)
    report_on_chain_hash = models.CharField(max_length=66, null=True, blank=True)
    certificate_tx_hash = models.CharField(max_length=66, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'audits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['contract_address']),
        ]

    def __str__(self):
        return f"{self.project.name} - {self.contract_address}"

class AuditFinding(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('informational', 'Informational'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='findings')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    category = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    description = models.TextField()
    location = models.CharField(max_length=500, blank=True)
    recommendation = models.TextField()
    code_snippet = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'audit_findings'
        ordering = ['severity']

    def __str__(self):
        return f"{self.severity.upper()} - {self.title}"
