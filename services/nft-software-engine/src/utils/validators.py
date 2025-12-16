"""
Input validation utilities for NFT Software Engine
"""

import re
from typing import Optional


def validate_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    if not address:
        return False
    
    # Remove '0x' prefix if present
    addr = address.replace('0x', '') if address.startswith('0x') else address
    
    # Check length (40 hex characters for address)
    if len(addr) != 40:
        return False
    
    # Check if all characters are valid hex
    return all(c in '0123456789abcdefABCDEF' for c in addr)


def validate_transaction_hash(tx_hash: str) -> bool:
    """Validate transaction hash format"""
    if not tx_hash:
        return False
    
    # Remove '0x' prefix if present
    hash_part = tx_hash.replace('0x', '') if tx_hash.startswith('0x') else tx_hash
    
    # Check length (64 hex characters for transaction hash)
    if len(hash_part) != 64:
        return False
    
    # Check if all characters are valid hex
    return all(c in '0123456789abcdefABCDEF' for c in hash_part)


def validate_token_id(token_id: str) -> bool:
    """Validate token ID format"""
    if not token_id:
        return False
    
    # Token ID should be a positive integer or hex string
    if token_id.isdigit():
        return int(token_id) >= 0
    
    # Check hex format
    hex_part = token_id.replace('0x', '') if token_id.startswith('0x') else token_id
    return hex_part.isdigit() and int(hex_part, 16) >= 0


def validate_contract_address(address: str) -> bool:
    """Validate contract address format"""
    return validate_ethereum_address(address)


def validate_network(network: str) -> bool:
    """Validate blockchain network"""
    valid_networks = [
        'ethereum', 'polygon', 'bsc', 'arbitrum', 'optimism',
        'mainnet', 'goerli', 'sepolia', 'polygon-mumbai'
    ]
    return network.lower() in valid_networks


def validate_tier_name(tier_name: str) -> bool:
    """Validate tier name format"""
    if not tier_name:
        return False
    
    # Check length and allowed characters
    return (
        len(tier_name) <= 50 and
        re.match(r'^[a-zA-Z0-9_-]+$', tier_name) is not None
    )


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(url_pattern, url) is not None


def validate_ens_name(ens_name: str) -> bool:
    """Validate ENS name format"""
    if not ens_name:
        return False
    
    # ENS names should end with .eth and be valid domain names
    if not ens_name.endswith('.eth'):
        return False
    
    # Remove .eth and validate the domain part
    domain_part = ens_name[:-4]  # Remove '.eth'
    
    # Basic domain validation
    return (
        len(domain_part) > 0 and
        len(domain_part) <= 63 and
        re.match(r'^[a-zA-Z0-9-]+$', domain_part) is not None and
        not domain_part.startswith('-') and
        not domain_part.endswith('-')
    )


def sanitize_address(address: str) -> Optional[str]:
    """Sanitize and normalize address"""
    if not address:
        return None
    
    # Remove spaces and convert to lowercase
    address = address.strip().lower()
    
    # Add '0x' prefix if not present
    if not address.startswith('0x'):
        address = '0x' + address
    
    # Validate
    if validate_ethereum_address(address):
        return address
    
    return None


def validate_amount(amount: str) -> bool:
    """Validate amount (price, gas fee, etc.)"""
    try:
        float_amount = float(amount)
        return float_amount >= 0
    except (ValueError, TypeError):
        return False


def validate_gas_price(gas_price: str) -> bool:
    """Validate gas price"""
    try:
        price = float(gas_price)
        return price > 0 and price < 10000  # Reasonable gas price range
    except (ValueError, TypeError):
        return False


def validate_gas_limit(gas_limit: str) -> bool:
    """Validate gas limit"""
    try:
        limit = int(gas_limit)
        return 21000 <= limit <= 10000000  # Reasonable gas limit range
    except (ValueError, TypeError):
        return False


def validate_metadata_uri(uri: str) -> bool:
    """Validate metadata URI"""
    if not uri:
        return True  # URI is optional
    
    # Can be HTTP/HTTPS URL or IPFS hash
    if uri.startswith('http://') or uri.startswith('https://'):
        return validate_url(uri)
    
    # IPFS hash validation
    if uri.startswith('ipfs://'):
        ipfs_hash = uri[7:]  # Remove 'ipfs://' prefix
        return len(ipfs_hash) > 0
    
    # Direct IPFS hash
    if len(uri) > 0:
        # IPFS hashes are typically 46 characters starting with 'Qm'
        return uri.startswith('Qm') and len(uri) == 46
    
    return False
