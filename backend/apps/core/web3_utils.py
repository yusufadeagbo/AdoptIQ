from web3 import Web3
from eth_account.messages import encode_defunct
from django.conf import settings
from django.core.cache import cache
import random

def get_web3_provider(chain='ethereum'):
    return Web3(Web3.HTTPProvider(settings.WEB3_PROVIDERS.get(chain)))

def verify_wallet_signature(wallet_address, signature, message):
    try:
        w3 = Web3()
        message_hash = encode_defunct(text=message)
        recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
        return recovered_address.lower() == wallet_address.lower()
    except Exception:
        return False

def generate_nonce():
    import secrets
    return secrets.token_hex(32)

def store_nonce(wallet_address, nonce, expiry=300):
    cache_key = f'nonce:{wallet_address.lower()}'
    cache.set(cache_key, nonce, expiry)

def verify_nonce(wallet_address, nonce):
    cache_key = f'nonce:{wallet_address.lower()}'
    stored_nonce = cache.get(cache_key)
    if stored_nonce == nonce:
        cache.delete(cache_key)
        return True
    return False

def get_transaction(chain, tx_hash):
    w3 = get_web3_provider(chain)
    try:
        return w3.eth.get_transaction(tx_hash)
    except Exception:
        return None

def get_transaction_receipt(chain, tx_hash):
    w3 = get_web3_provider(chain)
    try:
        return w3.eth.get_transaction_receipt(tx_hash)
    except Exception:
        return None

def get_contract(chain, address, abi):
    w3 = get_web3_provider(chain)
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

def get_block_number(chain):
    w3 = get_web3_provider(chain)
    return w3.eth.block_number

def get_logs(chain, from_block, to_block, address=None, topics=None):
    w3 = get_web3_provider(chain)
    filter_params = {
        'fromBlock': from_block,
        'toBlock': to_block,
    }
    if address:
        filter_params['address'] = Web3.to_checksum_address(address)
    if topics:
        filter_params['topics'] = topics

    return w3.eth.get_logs(filter_params)

def is_valid_address(address):
    return Web3.is_address(address)

def to_checksum_address(address):
    return Web3.to_checksum_address(address)

def wei_to_eth(wei):
    return Web3.from_wei(wei, 'ether')

def eth_to_wei(eth):
    return Web3.to_wei(eth, 'ether')
