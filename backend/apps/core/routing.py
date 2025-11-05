from django.urls import path
from apps.core.consumers import DashboardConsumer, MissionConsumer, AuditConsumer

websocket_urlpatterns = [
    path('ws/dashboard/', DashboardConsumer.as_asgi()),
    path('ws/missions/<uuid:mission_id>/', MissionConsumer.as_asgi()),
    path('ws/audits/<uuid:audit_id>/', AuditConsumer.as_asgi()),
]
