from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    health_status = {
        'status': 'healthy',
        'checks': {}
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = 'unhealthy'
        health_status['status'] = 'unhealthy'
        logger.error(f"Database health check failed: {str(e)}")

    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'healthy'
        else:
            health_status['checks']['cache'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['cache'] = 'unhealthy'
        logger.error(f"Cache health check failed: {str(e)}")

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)

def readiness_check(request):
    return JsonResponse({'status': 'ready'})

def liveness_check(request):
    return JsonResponse({'status': 'alive'})
