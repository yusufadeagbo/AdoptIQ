from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from apps.audits.models import Audit, AuditFinding
from apps.audits.serializers import AuditSerializer, AuditFindingSerializer
from apps.audits.tasks import process_audit
from apps.core.pagination import StandardResultsSetPagination
import os

class AuditViewSet(viewsets.ModelViewSet):
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Audit.objects.all()

        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def perform_create(self, serializer):
        audit = serializer.save()

        audit.complexity_score = self.calculate_complexity(audit)
        audit.price = self.calculate_price(audit.complexity_score)
        audit.save()

        process_audit.delay(str(audit.id))

    def calculate_complexity(self, audit):
        base_complexity = 50

        if audit.source_code:
            lines = len(audit.source_code.split('\n'))
            base_complexity += min(lines // 10, 200)

        return base_complexity

    def calculate_price(self, complexity_score):
        base_price = 100

        if complexity_score < 100:
            return base_price
        elif complexity_score < 200:
            return base_price * 2
        else:
            return base_price * 3

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        audit = self.get_object()

        if audit.status != 'completed':
            return Response({'error': 'Audit not completed yet'}, status=status.HTTP_400_BAD_REQUEST)

        if not audit.report_ipfs_hash:
            return Response({'error': 'Report not available'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'ipfs_hash': audit.report_ipfs_hash,
            'ipfs_url': f'https://ipfs.io/ipfs/{audit.report_ipfs_hash}',
            'on_chain_hash': audit.report_on_chain_hash,
            'certificate_tx': audit.certificate_tx_hash,
        })

    @action(detail=True, methods=['get'])
    def findings(self, request, pk=None):
        audit = self.get_object()
        findings = AuditFinding.objects.filter(audit=audit)

        severity = request.query_params.get('severity')
        if severity:
            findings = findings.filter(severity=severity)

        serializer = AuditFindingSerializer(findings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def dispute(self, request, pk=None):
        audit = self.get_object()
        finding_id = request.data.get('finding_id')
        reason = request.data.get('reason')

        if not all([finding_id, reason]):
            return Response({'error': 'finding_id and reason are required'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Dispute submitted for review'})
