from rest_framework import serializers
from apps.billing.models import Subscription, Payment, Invoice

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'subscription', 'amount', 'token', 'chain', 'transaction_hash',
                  'status', 'billing_date', 'confirmed_at', 'error_message', 'created_at']
        read_only_fields = ['id', 'status', 'confirmed_at', 'error_message', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    recent_payments = PaymentSerializer(many=True, read_only=True, source='payments')

    class Meta:
        model = Subscription
        fields = ['id', 'project', 'plan_tier', 'status', 'payment_token', 'payment_chain',
                  'wallet_address', 'amount_per_cycle', 'billing_cycle_days', 'next_billing_date',
                  'allowance_set', 'created_at', 'updated_at', 'recent_payments']
        read_only_fields = ['id', 'created_at', 'updated_at']

class InvoiceSerializer(serializers.ModelSerializer):
    payment_details = PaymentSerializer(source='payment', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'subscription', 'payment', 'payment_details', 'invoice_number',
                  'amount', 'due_date', 'paid_date', 'status', 'created_at']
        read_only_fields = ['id', 'invoice_number', 'paid_date', 'status', 'created_at']
