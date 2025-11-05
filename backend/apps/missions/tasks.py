from celery import shared_task
from django.utils import timezone
from apps.missions.models import Mission, Participation, MissionVerificationLog, BlockchainEvent
from apps.missions.fraud_detection import calculate_fraud_score, is_suspicious
from apps.core.web3_utils import get_transaction_receipt, get_logs, get_block_number
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@shared_task
def verify_participation(participation_id):
    try:
        participation = Participation.objects.get(id=participation_id)
    except Participation.DoesNotExist:
        logger.error(f"Participation {participation_id} not found")
        return

    mission = participation.mission
    chain = mission.chain

    try:
        participation.verification_attempts += 1
        participation.save()

        if not participation.transaction_hash:
            participation.status = 'rejected'
            participation.rejection_reason = 'No transaction hash provided'
            participation.save()
            return

        receipt = get_transaction_receipt(chain, participation.transaction_hash)
        if not receipt:
            if participation.verification_attempts >= 3:
                participation.status = 'rejected'
                participation.rejection_reason = 'Transaction not found after multiple attempts'
                participation.save()
            return

        if receipt.get('status') != 1:
            participation.status = 'rejected'
            participation.rejection_reason = 'Transaction failed'
            participation.save()
            return

        if not verify_mission_criteria(participation, receipt, mission.criteria):
            participation.status = 'rejected'
            participation.rejection_reason = 'Does not meet mission criteria'
            participation.save()
            return

        fraud_score = calculate_fraud_score(participation)
        participation.fraud_score = fraud_score

        suspicion_level = is_suspicious(fraud_score)

        if suspicion_level == 'high':
            participation.status = 'rejected'
            participation.rejection_reason = f'High fraud score: {fraud_score}'
            participation.save()

            logger.warning(f"Participation {participation_id} rejected due to high fraud score")
            return

        elif suspicion_level == 'medium':
            logger.info(f"Participation {participation_id} flagged for manual review (fraud score: {fraud_score})")

        participation.status = 'verified'
        participation.verified_at = timezone.now()
        participation.save()

        mission.current_participants += 1
        mission.save()

        MissionVerificationLog.objects.create(
            participation=participation,
            status='verified',
            details={'fraud_score': fraud_score}
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'mission_{mission.id}',
            {
                'type': 'participant_verified',
                'data': {
                    'event': 'participant.verified',
                    'mission_id': str(mission.id),
                    'participation_id': str(participation.id),
                    'wallet_address': participation.wallet_address,
                    'current_participants': mission.current_participants,
                }
            }
        )

        logger.info(f"Participation {participation_id} verified successfully")

    except Exception as e:
        logger.error(f"Error verifying participation {participation_id}: {str(e)}")
        participation.status = 'rejected'
        participation.rejection_reason = f'Verification error: {str(e)}'
        participation.save()

def verify_mission_criteria(participation, receipt, criteria):
    criteria_type = criteria.get('type')

    if criteria_type == 'token_transfer':
        return verify_token_transfer(participation, receipt, criteria)
    elif criteria_type == 'nft_mint':
        return verify_nft_mint(participation, receipt, criteria)
    elif criteria_type == 'contract_interaction':
        return verify_contract_interaction(participation, receipt, criteria)

    return True

def verify_token_transfer(participation, receipt, criteria):
    target_contract = criteria.get('contract_address', '').lower()
    min_amount = criteria.get('min_amount', 0)

    for log in receipt.get('logs', []):
        if log.get('address', '').lower() == target_contract:
            return True

    return False

def verify_nft_mint(participation, receipt, criteria):
    target_contract = criteria.get('contract_address', '').lower()

    for log in receipt.get('logs', []):
        if log.get('address', '').lower() == target_contract:
            topics = log.get('topics', [])
            if len(topics) > 0 and topics[0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                return True

    return False

def verify_contract_interaction(participation, receipt, criteria):
    target_contract = criteria.get('contract_address', '').lower()
    receipt_contract = receipt.get('to', '').lower()

    return receipt_contract == target_contract

@shared_task
def index_blockchain_events():
    active_missions = Mission.objects.filter(status='active')

    for mission in active_missions:
        try:
            index_mission_events(mission)
        except Exception as e:
            logger.error(f"Error indexing events for mission {mission.id}: {str(e)}")

def index_mission_events(mission):
    chain = mission.chain
    current_block = get_block_number(chain)

    last_indexed_block = mission.criteria.get('last_indexed_block', current_block - 1000)

    if current_block - last_indexed_block > 1000:
        to_block = last_indexed_block + 1000
    else:
        to_block = current_block

    contract_address = mission.criteria.get('contract_address')
    if not contract_address:
        return

    try:
        logs = get_logs(
            chain,
            from_block=last_indexed_block + 1,
            to_block=to_block,
            address=contract_address
        )

        for log in logs:
            BlockchainEvent.objects.get_or_create(
                chain=chain,
                transaction_hash=log['transactionHash'].hex(),
                defaults={
                    'block_number': log['blockNumber'],
                    'contract_address': log['address'],
                    'event_name': 'Transfer',
                    'event_data': {
                        'topics': [t.hex() for t in log.get('topics', [])],
                        'data': log.get('data', ''),
                    },
                    'processed': False,
                }
            )

        criteria = mission.criteria.copy()
        criteria['last_indexed_block'] = to_block
        mission.criteria = criteria
        mission.save()

    except Exception as e:
        logger.error(f"Error fetching logs for mission {mission.id}: {str(e)}")

@shared_task
def check_mission_completions():
    now = timezone.now()

    active_missions = Mission.objects.filter(
        status='active',
        end_date__lt=now
    )

    for mission in active_missions:
        mission.status = 'completed'
        mission.completed_at = now
        mission.save()

        logger.info(f"Mission {mission.id} marked as completed")

    return {'completed_missions': active_missions.count()}
