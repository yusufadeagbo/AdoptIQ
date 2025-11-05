from django.urls import path
from apps.analytics.views import DashboardStatsView, ProjectAnalyticsView, PlatformAnalyticsView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('project/<uuid:project_id>/', ProjectAnalyticsView.as_view(), name='project-analytics'),
    path('platform/', PlatformAnalyticsView.as_view(), name='platform-analytics'),
]
