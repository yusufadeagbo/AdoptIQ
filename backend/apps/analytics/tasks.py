from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum
from apps.missions.models import Mission, Participation
from apps.audits.models import Audit
from apps.billing.models import Payment
from apps.users.models import User, Project
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@shared_task
def aggregate_daily_stats():
    today = timezone.now().date()

    stats = {
        'date': today.isoformat(),
        'users': aggregate_user_stats(),
        'missions': aggregate_mission_stats(),
        'audits': aggregate_audit_stats(),
        'revenue': aggregate_revenue_stats(),
    }

    cache_key = f'daily_stats_{today.isoformat()}'
    cache.set(cache_key, stats, 86400 * 7)

    logger.info(f"Daily stats aggregated for {today}")

    return stats

def aggregate_user_stats():
    return {
        'total_users': User.objects.count(),
        'total_projects': Project.objects.count(),
        'active_users_7d': User.objects.filter(
            last_login_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
    }

def aggregate_mission_stats():
    return {
        'total_missions': Mission.objects.count(),
        'active_missions': Mission.objects.filter(status='active').count(),
        'completed_missions': Mission.objects.filter(status='completed').count(),
        'total_participants': Participation.objects.filter(status='verified').count(),
    }

def aggregate_audit_stats():
    return {
        'total_audits': Audit.objects.count(),
        'completed_audits': Audit.objects.filter(status='completed').count(),
        'total_findings': Audit.objects.aggregate(total=Sum('findings_count'))['total'] or 0,
    }

def aggregate_revenue_stats():
    return {
        'total_payments': Payment.objects.filter(status='confirmed').count(),
        'total_revenue': float(Payment.objects.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0),
    }
