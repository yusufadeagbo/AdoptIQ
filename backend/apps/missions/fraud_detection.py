from apps.core.web3_utils import get_web3_provider, get_transaction, get_transaction_receipt
from apps.missions.models import Participation
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def calculate_fraud_score(participation):
    score = 0.0
    wallet_address = participation.wallet_address
    mission = participation.mission

    score += check_transaction_timing(participation)
    score += check_gas_price_consistency(participation)
    score += check_wallet_funding(participation)
    score += check_wallet_age(participation)
    score += check_behavioral_patterns(participation)

    return min(score, 100.0)

def check_transaction_timing(participation):
    score = 0.0
    mission = participation.mission

    recent_participations = Participation.objects.filter(
        mission=mission,
        status='verified',
        verified_at__gte=timezone.now() - timedelta(minutes=5)
    ).exclude(id=participation.id)

    if recent_participations.count() >= 10:
        time_deltas = []
        prev_time = None

        for p in recent_participations.order_by('verified_at'):
            if prev_time:
                delta = (p.verified_at - prev_time).total_seconds()
                time_deltas.append(delta)
            prev_time = p.verified_at

        if time_deltas:
            avg_delta = sum(time_deltas) / len(time_deltas)
            if 50 < avg_delta < 70:
                score += 30.0
                logger.warning(f"Suspicious timing pattern detected for mission {mission.id}")

    return score

def check_gas_price_consistency(participation):
    score = 0.0

    if not participation.transaction_hash:
        return score

    try:
        chain = participation.mission.chain
        tx = get_transaction(chain, participation.transaction_hash)

        if tx:
            gas_price = tx.get('gasPrice', 0)

            recent_participations = Participation.objects.filter(
                mission=participation.mission,
                status='verified',
                transaction_hash__isnull=False
            ).exclude(id=participation.id)[:20]

            gas_prices = []
            for p in recent_participations:
                other_tx = get_transaction(chain, p.transaction_hash)
                if other_tx:
                    gas_prices.append(other_tx.get('gasPrice', 0))

            if gas_prices:
                matching_count = sum(1 for gp in gas_prices if gp == gas_price)
                if matching_count >= 10:
                    score += 25.0
                    logger.warning(f"Identical gas prices detected for participation {participation.id}")

    except Exception as e:
        logger.error(f"Error checking gas price: {str(e)}")

    return score

def check_wallet_funding(participation):
    score = 0.0

    try:
        chain = participation.mission.chain
        w3 = get_web3_provider(chain)

        wallet_address = participation.wallet_address

        participations_from_mission = Participation.objects.filter(
            mission=participation.mission,
            status='verified'
        ).exclude(id=participation.id)

        common_funder_count = 0

        for p in participations_from_mission[:50]:
            pass

    except Exception as e:
        logger.error(f"Error checking wallet funding: {str(e)}")

    return score

def check_wallet_age(participation):
    score = 0.0

    try:
        chain = participation.mission.chain
        w3 = get_web3_provider(chain)
        wallet_address = participation.wallet_address

        tx_count = w3.eth.get_transaction_count(wallet_address)

        if tx_count < 5:
            score += 20.0
        elif tx_count < 10:
            score += 10.0

    except Exception as e:
        logger.error(f"Error checking wallet age: {str(e)}")

    return score

def check_behavioral_patterns(participation):
    score = 0.0

    user_participations = Participation.objects.filter(
        wallet_address=participation.wallet_address
    ).exclude(id=participation.id)

    if user_participations.count() == 0:
        score += 5.0

    immediate_submissions = user_participations.filter(
        created_at=participation.created_at,
        status='verified'
    ).count()

    if immediate_submissions >= 3:
        score += 15.0

    return score

def is_suspicious(fraud_score):
    if fraud_score >= 70:
        return 'high'
    elif fraud_score >= 40:
        return 'medium'
    else:
        return 'low'
