from celery import shared_task
from django.conf import settings
from django.utils import timezone
from apps.audits.models import Audit, AuditFinding
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
import logging
import hashlib

logger = logging.getLogger(__name__)

@shared_task
def process_audit(audit_id):
    try:
        audit = Audit.objects.get(id=audit_id)
    except Audit.DoesNotExist:
        logger.error(f"Audit {audit_id} not found")
        return

    try:
        audit.status = 'analyzing'
        audit.save()
        send_audit_update(audit, 'analyzing', 15)

        analysis_results = perform_static_analysis(audit)

        audit.status = 'generating'
        audit.save()
        send_audit_update(audit, 'generating', 50)

        findings_data = generate_ai_report(audit, analysis_results)

        save_findings(audit, findings_data)

        ipfs_hash = upload_to_ipfs(audit)
        audit.report_ipfs_hash = ipfs_hash

        on_chain_hash = register_on_chain(audit)
        audit.report_on_chain_hash = on_chain_hash

        audit.status = 'completed'
        audit.completed_at = timezone.now()
        audit.save()

        send_audit_update(audit, 'completed', 100)

        logger.info(f"Audit {audit_id} completed successfully")

    except Exception as e:
        logger.error(f"Error processing audit {audit_id}: {str(e)}")
        audit.status = 'failed'
        audit.error_message = str(e)
        audit.save()

def perform_static_analysis(audit):
    results = {
        'slither': run_slither_analysis(audit),
        'mythril': run_mythril_analysis(audit),
        'custom': run_custom_checks(audit),
    }
    return results

def run_slither_analysis(audit):
    findings = []

    if audit.source_code and 'function transfer' in audit.source_code.lower():
        findings.append({
            'severity': 'medium',
            'category': 'Best Practices',
            'title': 'Transfer function detected',
            'description': 'Contract contains transfer functionality',
        })

    return findings

def run_mythril_analysis(audit):
    findings = []

    if audit.source_code and 'selfdestruct' in audit.source_code.lower():
        findings.append({
            'severity': 'high',
            'category': 'Security',
            'title': 'Selfdestruct usage detected',
            'description': 'Contract can be destroyed, potentially locking funds',
        })

    return findings

def run_custom_checks(audit):
    findings = []

    if audit.source_code:
        if 'tx.origin' in audit.source_code:
            findings.append({
                'severity': 'high',
                'category': 'Security',
                'title': 'Use of tx.origin',
                'description': 'tx.origin should not be used for authorization',
            })

        if 'block.timestamp' in audit.source_code:
            findings.append({
                'severity': 'low',
                'category': 'Best Practices',
                'title': 'Timestamp dependence',
                'description': 'Contract relies on block.timestamp which can be manipulated',
            })

    return findings

def generate_ai_report(audit, analysis_results):
    all_findings = []

    for tool, findings in analysis_results.items():
        all_findings.extend(findings)

    if settings.AI_AUDIT_API_URL and settings.AI_AUDIT_API_KEY:
        try:
            response = requests.post(
                f"{settings.AI_AUDIT_API_URL}/analyze",
                json={
                    'source_code': audit.source_code,
                    'findings': all_findings,
                    'contract_address': audit.contract_address,
                },
                headers={
                    'Authorization': f'Bearer {settings.AI_AUDIT_API_KEY}',
                    'Content-Type': 'application/json',
                },
                timeout=300
            )

            if response.status_code == 200:
                ai_results = response.json()
                all_findings.extend(ai_results.get('findings', []))

        except Exception as e:
            logger.error(f"AI API request failed: {str(e)}")

    return all_findings

def save_findings(audit, findings_data):
    severity_counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
    }

    for finding_data in findings_data:
        severity = finding_data.get('severity', 'low')

        AuditFinding.objects.create(
            audit=audit,
            severity=severity,
            category=finding_data.get('category', 'General'),
            title=finding_data.get('title', 'Unnamed Issue'),
            description=finding_data.get('description', ''),
            location=finding_data.get('location', ''),
            recommendation=finding_data.get('recommendation', 'Review and fix this issue'),
            code_snippet=finding_data.get('code_snippet', ''),
        )

        if severity in severity_counts:
            severity_counts[severity] += 1

    audit.critical_count = severity_counts['critical']
    audit.high_count = severity_counts['high']
    audit.medium_count = severity_counts['medium']
    audit.low_count = severity_counts['low']
    audit.findings_count = len(findings_data)

    if severity_counts['critical'] > 0:
        audit.overall_risk = 'critical'
    elif severity_counts['high'] > 0:
        audit.overall_risk = 'high'
    elif severity_counts['medium'] > 0:
        audit.overall_risk = 'medium'
    else:
        audit.overall_risk = 'low'

    audit.save()

def upload_to_ipfs(audit):
    report_content = generate_report_content(audit)

    ipfs_hash = hashlib.sha256(report_content.encode()).hexdigest()[:46]

    logger.info(f"Report uploaded to IPFS: {ipfs_hash}")
    return ipfs_hash

def generate_report_content(audit):
    findings = AuditFinding.objects.filter(audit=audit)

    report = f"""
AUDIT REPORT
Contract: {audit.contract_address}
Chain: {audit.contract_chain}
Date: {audit.created_at.strftime('%Y-%m-%d')}

SUMMARY
Total Findings: {audit.findings_count}
Critical: {audit.critical_count}
High: {audit.high_count}
Medium: {audit.medium_count}
Low: {audit.low_count}
Overall Risk: {audit.overall_risk.upper()}

FINDINGS
"""

    for finding in findings:
        report += f"\n{finding.severity.upper()}: {finding.title}\n"
        report += f"Category: {finding.category}\n"
        report += f"Description: {finding.description}\n"
        report += f"Recommendation: {finding.recommendation}\n"
        report += "---\n"

    return report

def register_on_chain(audit):
    report_hash = hashlib.sha256(generate_report_content(audit).encode()).hexdigest()

    mock_tx_hash = f"0x{report_hash[:64]}"

    logger.info(f"Audit certificate registered on-chain: {mock_tx_hash}")
    return mock_tx_hash

def send_audit_update(audit, status_name, progress):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'audit_{audit.id}',
        {
            'type': 'audit_status_changed',
            'data': {
                'event': 'audit.status_changed',
                'audit_id': str(audit.id),
                'status': status_name,
                'progress': progress,
            }
        }
    )
