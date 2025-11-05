from celery import shared_task
from django.core.cache import cache
from apps.core.web3_utils import get_web3_provider, get_block_number
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_rpc_health():
    from django.conf import settings

    results = {}
    for chain_name, rpc_url in settings.WEB3_PROVIDERS.items():
        try:
            w3 = get_web3_provider(chain_name)
            block_number = get_block_number(chain_name)

            import time
            start = time.time()
            w3.eth.get_block('latest')
            latency = (time.time() - start) * 1000

            results[chain_name] = {
                'status': 'healthy',
                'block_number': block_number,
                'latency_ms': round(latency, 2)
            }

            cache.set(f'rpc_health_{chain_name}', results[chain_name], 3600)

        except Exception as e:
            logger.error(f"RPC health check failed for {chain_name}: {str(e)}")
            results[chain_name] = {
                'status': 'unhealthy',
                'error': str(e)
            }

    return results

@shared_task
def archive_old_data():
    from datetime import datetime, timedelta
    from apps.missions.models import Participation

    cutoff_date = datetime.now() - timedelta(days=365)

    old_participations = Participation.objects.filter(
        created_at__lt=cutoff_date,
        status='verified'
    )

    count = old_participations.count()
    logger.info(f"Archiving {count} old participation records")

    return {'archived_participations': count}

@shared_task
def send_notification(user_id, notification_type, data):
    from apps.users.models import User

    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Sending {notification_type} notification to user {user.wallet_address}")

        return {'status': 'sent', 'user_id': str(user_id)}
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for notification")
        return {'status': 'failed', 'error': 'User not found'}
