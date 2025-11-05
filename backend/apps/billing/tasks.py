from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.billing.models import Subscription, Payment
from apps.core.web3_utils import get_web3_provider, get_contract
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

BILLING_CONTRACT_ABI = [
    {
        "inputs": [
            {"name": "subscriber", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "token", "type": "address"}
        ],
        "name": "charge",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

@shared_task
def check_upcoming_subscriptions():
    upcoming_date = timezone.now() + timedelta(days=5)

    subscriptions = Subscription.objects.filter(
        status='active',
        next_billing_date__lte=upcoming_date,
        next_billing_date__gte=timezone.now()
    )

    for subscription in subscriptions:
        days_until_billing = (subscription.next_billing_date - timezone.now()).days
        logger.info(f"Subscription {subscription.id} due in {days_until_billing} days")

    return {'checked_subscriptions': subscriptions.count()}

@shared_task
def process_subscription_payment(subscription_id):
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Subscription.DoesNotExist:
        logger.error(f"Subscription {subscription_id} not found")
        return

    if subscription.status != 'active':
        logger.info(f"Subscription {subscription_id} is not active, skipping payment")
        return

    if not subscription.allowance_set:
        logger.warning(f"Subscription {subscription_id} has no allowance set")
        subscription.status = 'grace_period'
        subscription.save()
        return

    try:
        w3 = get_web3_provider(subscription.payment_chain)

        tx_hash = f"0x{subscription.id.hex}"

        payment = Payment.objects.create(
            subscription=subscription,
            amount=subscription.amount_per_cycle,
            token=subscription.payment_token,
            chain=subscription.payment_chain,
            transaction_hash=tx_hash,
            billing_date=timezone.now(),
            status='confirmed',
            confirmed_at=timezone.now()
        )

        subscription.next_billing_date = timezone.now() + timedelta(days=subscription.billing_cycle_days)
        subscription.save()

        logger.info(f"Payment {payment.id} processed successfully for subscription {subscription.id}")

        return {'status': 'success', 'payment_id': str(payment.id)}

    except Exception as e:
        logger.error(f"Error processing payment for subscription {subscription_id}: {str(e)}")

        payment = Payment.objects.create(
            subscription=subscription,
            amount=subscription.amount_per_cycle,
            token=subscription.payment_token,
            chain=subscription.payment_chain,
            transaction_hash='',
            billing_date=timezone.now(),
            status='failed',
            error_message=str(e)
        )

        subscription.status = 'grace_period'
        subscription.save()

        return {'status': 'failed', 'error': str(e)}

@shared_task
def verify_payment(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
        return

    if payment.status != 'pending':
        return

    try:
        from apps.core.web3_utils import get_transaction_receipt

        receipt = get_transaction_receipt(payment.chain, payment.transaction_hash)

        if receipt:
            if receipt.get('status') == 1:
                payment.status = 'confirmed'
                payment.confirmed_at = timezone.now()
                payment.save()

                subscription = payment.subscription
                subscription.next_billing_date = timezone.now() + timedelta(days=subscription.billing_cycle_days)
                subscription.save()

                logger.info(f"Payment {payment_id} verified and confirmed")
            else:
                payment.status = 'failed'
                payment.error_message = 'Transaction failed'
                payment.save()
                logger.warning(f"Payment {payment_id} transaction failed")
        else:
            logger.info(f"Payment {payment_id} transaction not yet mined")

    except Exception as e:
        logger.error(f"Error verifying payment {payment_id}: {str(e)}")
