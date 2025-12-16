"""
Web3 client for multi-network token verification
"""

from web3 import Web3
from typing import Optional, Dict, List
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class Web3Client:
    """Multi-network Web3 client"""
    
    def __init__(self):
        self.clients: Dict[str, Web3] = {}
        self.contract_addresses: Dict[str, str] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Web3 clients for each network"""
        # #region agent log
        try:
            from .debug_log import debug_log
            debug_log("debug-session", "startup", "H5", "token-verification-service/src/web3_client.py:20", "Initializing Web3 clients", {"networks": ["ethereum", "polygon", "arbitrum"]})
        except Exception:
            pass
        # #endregion
        networks = {
            'ethereum': {
                'rpc': os.getenv('ETHEREUM_RPC_URL', 'https://rpc.sepolia.org'),
                'contract': os.getenv('LICENSE_TOKEN_CONTRACT_ETHEREUM', '')
            },
            'polygon': {
                'rpc': os.getenv('POLYGON_RPC_URL', 'https://rpc-mumbai.maticvigil.com'),
                'contract': os.getenv('LICENSE_TOKEN_CONTRACT_POLYGON', '')
            },
            'arbitrum': {
                'rpc': os.getenv('ARBITRUM_RPC_URL', 'https://goerli-rollup.arbitrum.io/rpc'),
                'contract': os.getenv('LICENSE_TOKEN_CONTRACT_ARBITRUM', '')
            }
        }
        
        for network, config in networks.items():
            try:
                # #region agent log
                try:
                    from .debug_log import debug_log
                    debug_log("debug-session", "startup", "H5", "token-verification-service/src/web3_client.py:35", "Connecting to network", {"network": network, "rpc_url": config['rpc']})
                except Exception:
                    pass
                # #endregion
                w3 = Web3(Web3.HTTPProvider(config['rpc']))
                # #region agent log
                is_connected = w3.is_connected()
                try:
                    from .debug_log import debug_log
                    debug_log("debug-session", "startup", "H5", "token-verification-service/src/web3_client.py:38", "Web3 connection check result", {"network": network, "connected": is_connected})
                except Exception:
                    pass
                # #endregion
                if is_connected:
                    self.clients[network] = w3
                    self.contract_addresses[network] = config['contract']
                    # #region agent log
                    try:
                        from .debug_log import debug_log
                        debug_log("debug-session", "startup", "H5", "token-verification-service/src/web3_client.py:42", "Network client initialized successfully", {"network": network})
                    except Exception:
                        pass
                    # #endregion
                    logger.info(f"Connected to {network} network")
                else:
                    # #region agent log
                    try:
                        from .debug_log import debug_log
                        debug_log("debug-session", "startup", "H5", "token-verification-service/src/web3_client.py:47", "Failed to connect to network", {"network": network})
                    except Exception:
                        pass
                    # #endregion
                    logger.warning(f"Failed to connect to {network} network")
            except Exception as e:
                # #region agent log
                try:
                    from .debug_log import debug_log
                    debug_log("debug-session", "startup", "H5", "token-verification-service/src/web3_client.py:50", "Error initializing network client", {"network": network, "error": str(e), "error_type": type(e).__name__})
                except Exception:
                    pass
                # #endregion
                logger.error(f"Error initializing {network} client: {str(e)}")
    
    def get_client(self, network: str) -> Optional[Web3]:
        """Get Web3 client for a specific network"""
        return self.clients.get(network)
    
    def get_contract_address(self, network: str) -> Optional[str]:
        """Get contract address for a specific network"""
        return self.contract_addresses.get(network)
    
    def verify_token_ownership(
        self,
        network: str,
        contract_address: str,
        wallet_address: str,
        token_id: int
    ) -> bool:
        """
        Verify that a wallet owns a specific token
        
        Args:
            network: Network name (ethereum, polygon, arbitrum)
            contract_address: ERC-721 contract address
            wallet_address: Wallet address to check
            token_id: Token ID to verify
            
        Returns:
            True if wallet owns the token, False otherwise
        """
        client = self.get_client(network)
        if not client:
            logger.error(f"No client available for network: {network}")
            return False
        
        try:
            # ERC-721 ownerOf function
            contract = client.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=self._get_erc721_abi()
            )
            
            owner = contract.functions.ownerOf(token_id).call()
            return owner.lower() == wallet_address.lower()
        except Exception as e:
            logger.error(f"Error verifying token ownership: {str(e)}")
            return False
    
    def get_token_tier(
        self,
        network: str,
        contract_address: str,
        token_id: int
    ) -> Optional[str]:
        """
        Get tier for a token
        
        Args:
            network: Network name
            contract_address: Contract address
            token_id: Token ID
            
        Returns:
            Tier string (bronze, silver, gold) or None
        """
        client = self.get_client(network)
        if not client:
            return None
        
        try:
            contract = client.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=self._get_license_token_abi()
            )
            
            tier = contract.functions.getTier(token_id).call()
            return tier
        except Exception as e:
            logger.error(f"Error getting token tier: {str(e)}")
            return None
    
    def get_user_tokens(
        self,
        network: str,
        contract_address: str,
        wallet_address: str
    ) -> List[Dict]:
        """
        Get all tokens owned by a wallet (simplified - in production, use events or indexer)
        
        Note: This is a simplified implementation. In production, you should:
        1. Use an indexer (The Graph, Alchemy, etc.)
        2. Listen to Transfer events
        3. Maintain a database of token ownership
        """
        # For now, return empty list
        # In production, implement proper token enumeration
        return []
    
    @staticmethod
    def _get_erc721_abi():
        """Get minimal ERC-721 ABI"""
        return [
            {
                "constant": True,
                "inputs": [{"name": "_tokenId", "type": "uint256"}],
                "name": "ownerOf",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]
    
    @staticmethod
    def _get_license_token_abi():
        """Get LicenseToken contract ABI"""
        return [
            {
                "constant": True,
                "inputs": [{"name": "_tokenId", "type": "uint256"}],
                "name": "ownerOf",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "tokenId", "type": "uint256"}],
                "name": "getTier",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "owner", "type": "address"},
                    {"name": "tokenId", "type": "uint256"}
                ],
                "name": "verifyLicense",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]


# Global instance
web3_client = Web3Client()

