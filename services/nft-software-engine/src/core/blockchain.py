"""
Blockchain interaction utilities for NFT Software Engine
"""

import logging
from typing import Optional, Dict, Any, List
from web3 import Web3
from eth_account import Account
import hexbytes

from ..config.settings import settings

logger = logging.getLogger(__name__)


class BlockchainClient:
    """Client for blockchain interactions"""
    
    def __init__(self, provider_url: str = None, private_key: str = None):
        self.provider_url = provider_url or settings.WEB3_PROVIDER_URL
        self.private_key = private_key or settings.PRIVATE_KEY
        self.w3 = None
        self.account = None
        self._connect()
    
    def _connect(self):
        """Connect to blockchain network"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
            
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to blockchain network")
            
            logger.info(f"Connected to blockchain network: {self.provider_url}")
            
            # Setup account if private key provided
            if self.private_key:
                self.account = Account.from_key(self.private_key)
                logger.info(f"Account loaded: {self.account.address}")
                
        except Exception as e:
            logger.error(f"Failed to connect to blockchain: {e}")
            raise
    
    def get_balance(self, address: str) -> Dict[str, str]:
        """Get account balance"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            return {
                "wei": str(balance_wei),
                "ether": str(balance_eth)
            }
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return {"wei": "0", "ether": "0"}
    
    def send_transaction(self, to_address: str, value: int = 0, data: str = None) -> Dict[str, Any]:
        """Send transaction"""
        if not self.account:
            raise ValueError("No account configured for transactions")
        
        try:
            # Build transaction
            transaction = {
                'to': to_address,
                'value': value,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': settings.GAS_LIMIT,
                'gasPrice': self.w3.to_wei(settings.GAS_PRICE, 'gwei'),
            }
            
            if data:
                transaction['data'] = data
            
            # Sign transaction
            signed_txn = self.account.sign_transaction(transaction)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            return {
                "transaction_hash": tx_hash.hex(),
                "status": tx_receipt.status,
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            }
            
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status"""
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "status": tx_receipt.status if tx_receipt else None,
                "block_number": tx_receipt.blockNumber if tx_receipt else None,
                "gas_used": tx_receipt.gasUsed if tx_receipt else None,
                "confirmed": tx_receipt is not None
            }
            
        except Exception as e:
            logger.error(f"Failed to get transaction status for {tx_hash}: {e}")
            return {"status": None, "confirmed": False}
    
    def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Estimate gas for transaction"""
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            return settings.GAS_LIMIT
    
    def get_gas_price(self) -> str:
        """Get current gas price"""
        try:
            gas_price_wei = self.w3.eth.gas_price
            gas_price_gwei = self.w3.from_wei(gas_price_wei, 'gwei')
            return str(gas_price_gwei)
        except Exception as e:
            logger.error(f"Failed to get gas price: {e}")
            return settings.GAS_PRICE


class WalletManager:
    """Manager for wallet connections"""
    
    def __init__(self, blockchain_client: BlockchainClient):
        self.blockchain = blockchain_client
    
    def validate_address(self, address: str) -> bool:
        """Validate Ethereum address format"""
        return self.blockchain.w3.is_address(address)
    
    def checksum_address(self, address: str) -> str:
        """Get checksum address"""
        return self.blockchain.w3.to_checksum_address(address)
    
    def get_wallet_tokens(self, address: str, contract_address: str = None) -> List[Dict[str, Any]]:
        """Get tokens in wallet (placeholder for future implementation)"""
        # This would be implemented with contract interaction
        # For now, return empty list
        return []
    
    def get_wallet_nfts(self, address: str) -> List[Dict[str, Any]]:
        """Get NFTs in wallet (placeholder for future implementation)"""
        # This would be implemented with contract interaction
        # For now, return empty list
        return []


class TransactionManager:
    """Manager for blockchain transactions"""
    
    def __init__(self, blockchain_client: BlockchainClient):
        self.blockchain = blockchain_client
    
    async def wait_for_confirmation(self, tx_hash: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for transaction confirmation"""
        import asyncio
        
        try:
            receipt = await asyncio.wait_for(
                self.blockchain.w3.eth.wait_for_transaction_receipt(tx_hash),
                timeout=timeout
            )
            
            return {
                "status": receipt.status,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "confirmed": True
            }
            
        except asyncio.TimeoutError:
            logger.warning(f"Transaction {tx_hash} timeout after {timeout} seconds")
            return {"status": None, "confirmed": False}
        except Exception as e:
            logger.error(f"Transaction confirmation error: {e}")
            return {"status": None, "confirmed": False}
