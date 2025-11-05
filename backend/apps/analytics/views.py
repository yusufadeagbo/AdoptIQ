from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from apps.missions.models import Mission, Participation
from apps.audits.models import Audit
from apps.billing.models import Subscription, Payment
from apps.users.models import User, Project

class DashboardStatsView(APIView):
    def get(self, request):
        user = request.user
        time_range = request.query_params.get('range', '30d')

        days = int(time_range.replace('d', ''))
        start_date = timezone.now() - timedelta(days=days)

        user_projects = Project.objects.filter(user=user)

        stats = {
            'overview': self.get_overview_stats(user, user_projects, start_date),
            'missions': self.get_mission_stats(user_projects, start_date),
            'audits': self.get_audit_stats(user_projects, start_date),
            'billing': self.get_billing_stats(user_projects, start_date),
        }

        return Response(stats)

    def get_overview_stats(self, user, projects, start_date):
        return {
            'total_projects': projects.count(),
            'active_missions': Mission.objects.filter(project__in=projects, status='active').count(),
            'total_participants': Participation.objects.filter(mission__project__in=projects, status='verified').count(),
            'completed_audits': Audit.objects.filter(project__in=projects, status='completed').count(),
        }

    def get_mission_stats(self, projects, start_date):
        missions = Mission.objects.filter(project__in=projects, created_at__gte=start_date)

        return {
            'total_missions': missions.count(),
            'active_missions': missions.filter(status='active').count(),
            'completed_missions': missions.filter(status='completed').count(),
            'total_participants': Participation.objects.filter(mission__in=missions, status='verified').count(),
            'avg_completion_rate': self.calculate_avg_completion_rate(missions),
        }

    def calculate_avg_completion_rate(self, missions):
        if not missions.exists():
            return 0

        total_rate = 0
        count = 0

        for mission in missions:
            if mission.target_participants > 0:
                rate = (mission.current_participants / mission.target_participants) * 100
                total_rate += rate
                count += 1

        return round(total_rate / count, 2) if count > 0 else 0

    def get_audit_stats(self, projects, start_date):
        audits = Audit.objects.filter(project__in=projects, created_at__gte=start_date)

        return {
            'total_audits': audits.count(),
            'completed_audits': audits.filter(status='completed').count(),
            'pending_audits': audits.filter(status__in=['pending', 'analyzing', 'generating']).count(),
            'total_findings': audits.aggregate(total=Sum('findings_count'))['total'] or 0,
            'critical_findings': audits.aggregate(total=Sum('critical_count'))['total'] or 0,
        }

    def get_billing_stats(self, projects, start_date):
        subscriptions = Subscription.objects.filter(project__in=projects)
        payments = Payment.objects.filter(subscription__in=subscriptions, created_at__gte=start_date)

        return {
            'active_subscriptions': subscriptions.filter(status='active').count(),
            'total_payments': payments.filter(status='confirmed').count(),
            'total_spent': float(payments.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0),
        }

class ProjectAnalyticsView(APIView):
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        time_range = request.query_params.get('range', '30d')
        days = int(time_range.replace('d', ''))
        start_date = timezone.now() - timedelta(days=days)

        analytics = {
            'project': {
                'id': str(project.id),
                'name': project.name,
                'category': project.category,
            },
            'missions': self.get_project_mission_analytics(project, start_date),
            'audits': self.get_project_audit_analytics(project, start_date),
            'growth': self.get_growth_metrics(project, start_date),
        }

        return Response(analytics)

    def get_project_mission_analytics(self, project, start_date):
        missions = Mission.objects.filter(project=project, created_at__gte=start_date)

        return {
            'total': missions.count(),
            'by_status': missions.values('status').annotate(count=Count('id')),
            'by_category': missions.values('category').annotate(count=Count('id')),
            'total_participants': Participation.objects.filter(mission__in=missions, status='verified').count(),
        }

    def get_project_audit_analytics(self, project, start_date):
        audits = Audit.objects.filter(project=project, created_at__gte=start_date)

        return {
            'total': audits.count(),
            'completed': audits.filter(status='completed').count(),
            'avg_risk_score': self.calculate_avg_risk_score(audits),
            'total_findings': audits.aggregate(total=Sum('findings_count'))['total'] or 0,
        }

    def calculate_avg_risk_score(self, audits):
        risk_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        total_score = 0
        count = 0

        for audit in audits.filter(overall_risk__isnull=False):
            total_score += risk_mapping.get(audit.overall_risk, 0)
            count += 1

        return round(total_score / count, 2) if count > 0 else 0

    def get_growth_metrics(self, project, start_date):
        missions = Mission.objects.filter(project=project, created_at__gte=start_date)

        daily_participants = []
        current_date = start_date.date()
        end_date = timezone.now().date()

        while current_date <= end_date:
            count = Participation.objects.filter(
                mission__project=project,
                verified_at__date=current_date
            ).count()

            daily_participants.append({
                'date': current_date.isoformat(),
                'count': count
            })

            current_date += timedelta(days=1)

        return {
            'daily_participants': daily_participants,
            'total_growth': sum(d['count'] for d in daily_participants),
        }

class PlatformAnalyticsView(APIView):
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        time_range = request.query_params.get('range', '30d')
        days = int(time_range.replace('d', ''))
        start_date = timezone.now() - timedelta(days=days)

        analytics = {
            'users': self.get_user_analytics(start_date),
            'missions': self.get_platform_mission_analytics(start_date),
            'audits': self.get_platform_audit_analytics(start_date),
            'revenue': self.get_revenue_analytics(start_date),
        }

        return Response(analytics)

    def get_user_analytics(self, start_date):
        return {
            'total_users': User.objects.count(),
            'new_users': User.objects.filter(created_at__gte=start_date).count(),
            'active_users': User.objects.filter(last_login_at__gte=start_date).count(),
            'total_projects': Project.objects.count(),
        }

    def get_platform_mission_analytics(self, start_date):
        missions = Mission.objects.filter(created_at__gte=start_date)

        return {
            'total_missions': missions.count(),
            'active_missions': missions.filter(status='active').count(),
            'total_participants': Participation.objects.filter(created_at__gte=start_date, status='verified').count(),
        }

    def get_platform_audit_analytics(self, start_date):
        audits = Audit.objects.filter(created_at__gte=start_date)

        return {
            'total_audits': audits.count(),
            'completed_audits': audits.filter(status='completed').count(),
            'total_findings': audits.aggregate(total=Sum('findings_count'))['total'] or 0,
        }

    def get_revenue_analytics(self, start_date):
        payments = Payment.objects.filter(created_at__gte=start_date, status='confirmed')

        return {
            'total_payments': payments.count(),
            'total_revenue': float(payments.aggregate(total=Sum('amount'))['total'] or 0),
            'active_subscriptions': Subscription.objects.filter(status='active').count(),
        }
