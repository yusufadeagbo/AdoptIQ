import os
from celery import Celery
from celery.schedules import crontab

os.setdefault('DJANGO_SETTINGS_MODULE', 'adoptiq.settings')

app = Celery('adoptiq')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-subscriptions-daily': {
        'task': 'apps.billing.tasks.check_upcoming_subscriptions',
        'schedule': crontab(hour=0, minute=0),
    },
    'aggregate-analytics-daily': {
        'task': 'apps.analytics.tasks.aggregate_daily_stats',
        'schedule': crontab(hour=1, minute=0),
    },
    'check-mission-completions': {
        'task': 'apps.missions.tasks.check_mission_completions',
        'schedule': crontab(hour=2, minute=0),
    },
    'archive-old-data': {
        'task': 'apps.core.tasks.archive_old_data',
        'schedule': crontab(hour=3, minute=0),
    },
    'index-blockchain-events': {
        'task': 'apps.missions.tasks.index_blockchain_events',
        'schedule': crontab(minute='*/5'),
    },
    'check-rpc-health': {
        'task': 'apps.core.tasks.check_rpc_health',
        'schedule': crontab(hour='*/6', minute=0),
    },
}

app.conf.task_routes = {
    'apps.billing.tasks.*': {'queue': 'high_priority'},
    'apps.missions.tasks.verify_*': {'queue': 'medium_priority'},
    'apps.audits.tasks.*': {'queue': 'medium_priority'},
    'apps.analytics.tasks.*': {'queue': 'low_priority'},
}
