"""
Smart contract abstractions for NFT Software Engine
"""

import logging
from typing import Dict, Any, Optional, List
from web3 import Web3
from eth_account import Account
import json

from .blockchain import BlockchainClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ContractInterface:
    """Interface for smart contract interactions"""
    
    def __init__(self, contract_address: str, abi: List[Dict] = None):
        self.contract_address = contract_address
        self.abi = abi or self._get_default_abi()
        self.contract = None
        self.blockchain = BlockchainClient()
        self._initialize_contract()
    
    def _initialize_contract(self):
        """Initialize contract interface"""
        try:
            self.contract = self.blockchain.w3.eth.contract(
                address=self.contract_address,
                abi=self.abi
            )
            logger.info(f"Contract initialized: {self.contract_address}")
        except Exception as e:
            logger.error(f"Failed to initialize contract {self.contract_address}: {e}")
            raise
    
    def _get_default_abi(self) -> List[Dict]:
        """Get default ERC721 contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "tokenId", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "operator", "type": "address"},
                    {"name": "approved", "type": "bool"}
                ],
                "name": "setApprovalForAll",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "ownerOf",
                "outputs": [{"name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "tokenId", "type": "uint256"}
                ],
                "name": "transferFrom",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "uri", "type": "string"}
                ],
                "name": "mintToken",
                "outputs": [{"name": "tokenId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "tokenURI",
                "outputs": [{"name": "", "type": "string"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def mint_token(self, to_address: str, token_uri: str) -> Dict[str, Any]:
        """Mint new token"""
        try:
            # Build transaction
            transaction = self.contract.functions.mintToken(
                to_address,
                token_uri
            ).build_transaction({
                'from': self.blockchain.account.address,
                'nonce': self.blockchain.w3.eth.get_transaction_count(self.blockchain.account.address),
                'gas': settings.GAS_LIMIT,
                'gasPrice': self.blockchain.w3.to_wei(settings.GAS_PRICE, 'gwei'),
            })
            
            # Sign and send transaction
            signed_txn = self.blockchain.account.sign_transaction(transaction)
            tx_hash = self.blockchain.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            receipt = self.blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse token ID from event logs
            token_id = None
            if receipt.logs:
                try:
                    # Extract token ID from mint event
                    event = self.contract.events.Transfer().process_receipt(receipt)
                    if event:
                        token_id = str(event[0]['args']['tokenId'])
                except Exception as e:
                    logger.warning(f"Failed to parse token ID: {e}")
            
            return {
                "transaction_hash": tx_hash.hex(),
                "token_id": token_id,
                "status": receipt.status,
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber
            }
            
        except Exception as e:
            logger.error(f"Mint token failed: {e}")
            raise
    
    def transfer_token(self, from_address: str, to_address: str, token_id: int) -> Dict[str, Any]:
        """Transfer token between addresses"""
        try:
            # Build transaction
            transaction = self.contract.functions.transferFrom(
                from_address,
                to_address,
                token_id
            ).build_transaction({
                'from': self.blockchain.account.address,
                'nonce': self.blockchain.w3.eth.get_transaction_count(self.blockchain.account.address),
                'gas': settings.GAS_LIMIT,
                'gasPrice': self.blockchain.w3.to_wei(settings.GAS_PRICE, 'gwei'),
            })
            
            # Sign and send transaction
            signed_txn = self.blockchain.account.sign_transaction(transaction)
            tx_hash = self.blockchain.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            receipt = self.blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": tx_hash.hex(),
                "status": receipt.status,
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber
            }
            
        except Exception as e:
            logger.error(f"Transfer token failed: {e}")
            raise
    
    def get_token_owner(self, token_id: int) -> Optional[str]:
        """Get current owner of token"""
        try:
            return self.contract.functions.ownerOf(token_id).call()
        except Exception as e:
            logger.error(f"Failed to get token owner for {token_id}: {e}")
            return None
    
    def get_token_uri(self, token_id: int) -> Optional[str]:
        """Get token URI"""
        try:
            return self.contract.functions.tokenURI(token_id).call()
        except Exception as e:
            logger.error(f"Failed to get token URI for {token_id}: {e}")
            return None
    
    def get_balance(self, address: str) -> int:
        """Get token balance for address"""
        try:
            return self.contract.functions.balanceOf(address).call()
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            return 0
    
    def get_total_supply(self) -> int:
        """Get total token supply"""
        try:
            return self.contract.functions.totalSupply().call()
        except Exception as e:
            logger.error(f"Failed to get total supply: {e}")
            return 0


class TieredNFTContract(ContractInterface):
    """Specialized contract for tiered NFT products"""
    
    def __init__(self, contract_address: str):
        super().__init__(contract_address)
        self._load_tier_functions()
    
    def _load_tier_functions(self):
        """Load tier-specific contract functions"""
        # Additional ABI for tiered NFT functionality
        tier_abi = [
            {
                "inputs": [{"name": "tier", "type": "uint8"}],
                "name": "getTierSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "tier", "type": "uint8"}
                ],
                "name": "mintTierToken",
                "outputs": [{"name": "tokenId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "getTokenTier",
                "outputs": [{"name": "tier", "type": "uint8"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Extend contract with tier functions
        for func in tier_abi:
            self.abi.append(func)
        
        # Re-initialize contract with extended ABI
        self._initialize_contract()
    
    def mint_tier_token(self, to_address: str, tier: int, token_uri: str) -> Dict[str, Any]:
        """Mint token for specific tier"""
        try:
            transaction = self.contract.functions.mintTierToken(to_address, tier).build_transaction({
                'from': self.blockchain.account.address,
                'nonce': self.blockchain.w3.eth.get_transaction_count(self.blockchain.account.address),
                'gas': settings.GAS_LIMIT,
                'gasPrice': self.blockchain.w3.to_wei(settings.GAS_PRICE, 'gwei'),
            })
            
            signed_txn = self.blockchain.account.sign_transaction(transaction)
            tx_hash = self.blockchain.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Parse token ID from event logs
            token_id = None
            if receipt.logs:
                try:
                    event = self.contract.events.Transfer().process_receipt(receipt)
                    if event:
                        token_id = str(event[0]['args']['tokenId'])
                except Exception as e:
                    logger.warning(f"Failed to parse token ID: {e}")
            
            return {
                "transaction_hash": tx_hash.hex(),
                "token_id": token_id,
                "tier": tier,
                "status": receipt.status,
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber
            }
            
        except Exception as e:
            logger.error(f"Mint tier token failed: {e}")
            raise
    
    def get_tier_supply(self, tier: int) -> int:
        """Get supply for specific tier"""
        try:
            return self.contract.functions.getTierSupply(tier).call()
        except Exception as e:
            logger.error(f"Failed to get tier supply for {tier}: {e}")
            return 0
    
    def get_token_tier(self, token_id: int) -> Optional[int]:
        """Get tier for specific token"""
        try:
            return self.contract.functions.getTokenTier(token_id).call()
        except Exception as e:
            logger.error(f"Failed to get token tier for {token_id}: {e}")
            return None
