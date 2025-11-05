from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from apps.billing.models import Subscription, Payment, Invoice
from apps.billing.serializers import SubscriptionSerializer, PaymentSerializer, InvoiceSerializer
from apps.billing.tasks import process_subscription_payment
from apps.core.pagination import StandardResultsSetPagination
from django.conf import settings

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Subscription.objects.filter(project__user=self.request.user)
        return Subscription.objects.none()

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        project_id = request.data.get('project_id')
        plan_tier = request.data.get('plan_tier')
        payment_token = request.data.get('payment_token', 'USDC')
        payment_chain = request.data.get('payment_chain', 'ethereum')
        wallet_address = request.data.get('wallet_address')

        if not all([project_id, plan_tier, wallet_address]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.users.models import Project
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(project, 'subscription'):
            return Response({'error': 'Project already has a subscription'}, status=status.HTTP_400_BAD_REQUEST)

        plan_config = settings.SUBSCRIPTION_PLANS.get(plan_tier)
        if not plan_config:
            return Response({'error': 'Invalid plan tier'}, status=status.HTTP_400_BAD_REQUEST)

        subscription = Subscription.objects.create(
            project=project,
            plan_tier=plan_tier,
            payment_token=payment_token,
            payment_chain=payment_chain,
            wallet_address=wallet_address,
            amount_per_cycle=plan_config['price_usd'],
            next_billing_date=timezone.now() + timedelta(days=30)
        )

        return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'])
    def update_plan(self, request, pk=None):
        subscription = self.get_object()
        new_plan_tier = request.data.get('plan_tier')

        if not new_plan_tier:
            return Response({'error': 'plan_tier is required'}, status=status.HTTP_400_BAD_REQUEST)

        plan_config = settings.SUBSCRIPTION_PLANS.get(new_plan_tier)
        if not plan_config:
            return Response({'error': 'Invalid plan tier'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.plan_tier = new_plan_tier
        subscription.amount_per_cycle = plan_config['price_usd']
        subscription.save()

        return Response(SubscriptionSerializer(subscription).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'canceled'
        subscription.save()

        return Response({'message': 'Subscription canceled'})

    @action(detail=True, methods=['post'])
    def set_allowance(self, request, pk=None):
        subscription = self.get_object()
        transaction_hash = request.data.get('transaction_hash')

        if not transaction_hash:
            return Response({'error': 'transaction_hash is required'}, status=status.HTTP_400_BAD_REQUEST)

        subscription.allowance_set = True
        subscription.save()

        return Response({'message': 'Allowance set successfully'})

    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from apps.users.models import Project
            project = Project.objects.get(id=project_id, user=request.user)
            subscription = Subscription.objects.get(project=project)
            return Response(SubscriptionSerializer(subscription).data)
        except (Project.DoesNotExist, Subscription.DoesNotExist):
            return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Payment.objects.filter(subscription__project__user=self.request.user)
        return Payment.objects.none()

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Invoice.objects.filter(subscription__project__user=self.request.user)
        return Invoice.objects.none()
