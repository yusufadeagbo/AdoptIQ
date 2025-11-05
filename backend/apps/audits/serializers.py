from rest_framework import serializers
from apps.audits.models import Audit, AuditFinding
from apps.users.serializers import ProjectSerializer

class AuditFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditFinding
        fields = ['id', 'audit', 'severity', 'category', 'title', 'description',
                  'location', 'recommendation', 'code_snippet']
        read_only_fields = ['id', 'audit']

class AuditSerializer(serializers.ModelSerializer):
    project_details = ProjectSerializer(source='project', read_only=True)
    findings = AuditFindingSerializer(many=True, read_only=True)

    class Meta:
        model = Audit
        fields = ['id', 'project', 'project_details', 'contract_address', 'contract_chain',
                  'source_code', 'compiler_version', 'complexity_score', 'status', 'price',
                  'payment_status', 'findings_count', 'critical_count', 'high_count',
                  'medium_count', 'low_count', 'overall_risk', 'report_ipfs_hash',
                  'report_on_chain_hash', 'certificate_tx_hash', 'error_message',
                  'created_at', 'completed_at', 'findings']
        read_only_fields = ['id', 'complexity_score', 'status', 'findings_count',
                            'critical_count', 'high_count', 'medium_count', 'low_count',
                            'overall_risk', 'report_ipfs_hash', 'report_on_chain_hash',
                            'certificate_tx_hash', 'created_at', 'completed_at']
