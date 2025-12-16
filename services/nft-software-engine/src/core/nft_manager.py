"""
NFT token management for NFT Software Engine
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .contracts import TieredNFTContract, ContractInterface
from .blockchain import BlockchainClient
from ..models.database import Product, Tier, TokenTransaction, TransactionStatus, PaymentMethod
from ..models.schemas import TokenVerificationResponse, TokenMetadata
from ..config.settings import settings

logger = logging.getLogger(__name__)


class NFTManager:
    """Manager for NFT token operations"""
    
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.blockchain = BlockchainClient()
    
    def verify_token_ownership(
        self,
        wallet_address: str,
        product_id: int,
        tier: str = None
    ) -> TokenVerificationResponse:
        """Verify if wallet owns token for product/tier"""
        try:
            # Get product and contract info
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            if not product or not product.contract_address:
                return TokenVerificationResponse(
                    has_token=False,
                    max_supply_reached=True
                )
            
            # Initialize contract interface
            if product.contract_type.value == "tiered":
                contract = TieredNFTContract(product.contract_address)
            else:
                contract = ContractInterface(product.contract_address)
            
            # Get wallet balance
            balance = contract.get_balance(wallet_address)
            
            if balance == 0:
                return TokenVerificationResponse(
                    has_token=False
                )
            
            # If specific tier requested, verify tier ownership
            if tier:
                token_tier = self._get_user_tier(wallet_address, contract, tier)
                if token_tier is None:
                    return TokenVerificationResponse(
                        has_token=False
                    )
                
                # Get token ID for this tier
                token_id = self._get_token_id_for_tier(wallet_address, contract, tier)
                
                return TokenVerificationResponse(
                    has_token=True,
                    tier=tier,
                    token_id=token_id,
                    features=self._get_tier_features(product, tier)
                )
            
            # Get highest tier owned by user
            user_tier = self._get_highest_user_tier(wallet_address, contract)
            if user_tier is None:
                return TokenVerificationResponse(
                    has_token=False
                )
            
            token_id = self._get_token_id_for_tier(wallet_address, contract, user_tier)
            
            return TokenVerificationResponse(
                has_token=True,
                tier=user_tier,
                token_id=token_id,
                features=self._get_tier_features(product, user_tier)
            )
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return TokenVerificationResponse(
                has_token=False,
                transaction_pending=True
            )
    
    def purchase_token(
        self,
        product_id: int,
        tier: str,
        wallet_address: str,
        user_id: int = None,
        payment_method: str = "crypto"
    ) -> Dict[str, Any]:
        """Purchase NFT token"""
        try:
            # Get product and tier info
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            tier_config = self.db_session.query(Tier).filter(
                Tier.product_id == product_id,
                Tier.name == tier
            ).first()
            
            if not product or not tier_config:
                raise ValueError("Product or tier not found")
            
            # Check if contract is deployed
            if not product.contract_address:
                raise ValueError("Smart contract not deployed for this product")
            
            # Check supply limits
            if tier_config.max_supply:
                current_supply = self._get_tier_supply(product.contract_address, tier)
                if current_supply >= tier_config.max_supply:
                    raise ValueError(f"Tier {tier} is sold out")
            
            # Create contract interface
            if product.contract_type.value == "tiered":
                contract = TieredNFTContract(product.contract_address)
                tier_number = self._get_tier_number(tier)
                result = contract.mint_tier_token(
                    wallet_address,
                    tier_number,
                    f"{settings.NFT_BASE_URI}{product.id}/{tier}"
                )
            else:
                contract = ContractInterface(product.contract_address)
                result = contract.mint_token(
                    wallet_address,
                    f"{settings.NFT_BASE_URI}{product.id}/{tier}"
                )
            
            # Create database transaction record
            transaction = TokenTransaction(
                product_id=product_id,
                tier_id=tier_config.id,
                user_id=user_id,
                wallet_address=wallet_address,
                token_id=result.get("token_id"),
                transaction_hash=result["transaction_hash"],
                payment_method=PaymentMethod(payment_method),
                amount=tier_config.price,
                crypto_amount=result.get("crypto_amount", tier_config.price),
                crypto_currency=product.currency,
                status=TransactionStatus.PENDING,
                gas_fee=result.get("gas_fee"),
                metadata_uri=f"{settings.NFT_BASE_URI}{product.id}/{tier}"
            )
            
            self.db_session.add(transaction)
            self.db_session.commit()
            
            logger.info(f"Token purchased: {result['transaction_hash']}")
            
            return {
                "transaction_hash": result["transaction_hash"],
                "token_id": result.get("token_id"),
                "status": "pending",
                "tier": tier,
                "product_id": product_id
            }
            
        except Exception as e:
            logger.error(f"Token purchase failed: {e}")
            # Rollback any database changes
            self.db_session.rollback()
            raise
    
    def transfer_token(
        self,
        token_id: str,
        from_wallet: str,
        to_wallet: str
    ) -> Dict[str, Any]:
        """Transfer NFT token between wallets"""
        try:
            # Get transaction info to find contract
            transaction = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.token_id == token_id
            ).first()
            
            if not transaction:
                raise ValueError("Token not found")
            
            product = self.db_session.query(Product).filter(
                Product.id == transaction.product_id
            ).first()
            
            if not product or not product.contract_address:
                raise ValueError("Contract not found")
            
            # Create contract interface and transfer
            if product.contract_type.value == "tiered":
                contract = TieredNFTContract(product.contract_address)
            else:
                contract = ContractInterface(product.contract_address)
            
            result = contract.transfer_token(
                from_wallet,
                to_wallet,
                int(token_id)
            )
            
            # Update transaction record
            transaction.status = TransactionStatus.CONFIRMED
            transaction.block_number = result["block_number"]
            self.db_session.commit()
            
            logger.info(f"Token transferred: {result['transaction_hash']}")
            
            return {
                "transaction_hash": result["transaction_hash"],
                "status": "confirmed",
                "from": from_wallet,
                "to": to_wallet
            }
            
        except Exception as e:
            logger.error(f"Token transfer failed: {e}")
            self.db_session.rollback()
            raise
    
    def get_user_tokens(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Get all tokens owned by wallet"""
        try:
            tokens = []
            
            # Get all transactions for this wallet
            transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.wallet_address == wallet_address,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).all()
            
            for transaction in transactions:
                product = self.db_session.query(Product).filter(
                    Product.id == transaction.product_id
                ).first()
                
                tier = self.db_session.query(Tier).filter(
                    Tier.id == transaction.tier_id
                ).first()
                
                tokens.append({
                    "token_id": transaction.token_id,
                    "product_id": transaction.product_id,
                    "product_name": product.name if product else "Unknown",
                    "tier": tier.name if tier else "Unknown",
                    "tier_type": tier.tier_type.value if tier and tier.tier_type else "unknown",
                    "acquired_at": transaction.created_at,
                    "transaction_hash": transaction.transaction_hash
                })
            
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to get user tokens: {e}")
            return []
    
    def _get_user_tier(self, wallet_address: str, contract: ContractInterface, tier: str) -> Optional[str]:
        """Get user's tier from contract"""
        try:
            # This would be implemented based on specific contract logic
            # For now, return the requested tier if user has balance
            balance = contract.get_balance(wallet_address)
            if balance > 0:
                return tier
            return None
        except Exception as e:
            logger.error(f"Failed to get user tier: {e}")
            return None
    
    def _get_highest_user_tier(self, wallet_address: str, contract: ContractInterface) -> Optional[str]:
        """Get highest tier owned by user"""
        try:
            # Check if user has any tokens
            balance = contract.get_balance(wallet_address)
            if balance == 0:
                return None
            
            # Return highest tier - this would be based on contract logic
            # For now, return a default
            return "gold"
        except Exception as e:
            logger.error(f"Failed to get highest user tier: {e}")
            return None
    
    def _get_token_id_for_tier(self, wallet_address: str, contract: ContractInterface, tier: str) -> Optional[str]:
        """Get token ID for specific tier owned by wallet"""
        try:
            # This would iterate through user's tokens to find the right tier
            # For now, return a placeholder
            return "1"
        except Exception as e:
            logger.error(f"Failed to get token ID for tier: {e}")
            return None
    
    def _get_tier_supply(self, contract_address: str, tier: str) -> int:
        """Get current supply for tier"""
        try:
            contract = TieredNFTContract(contract_address)
            tier_number = self._get_tier_number(tier)
            return contract.get_tier_supply(tier_number)
        except Exception as e:
            logger.error(f"Failed to get tier supply: {e}")
            return 0
    
    def _get_tier_number(self, tier: str) -> int:
        """Convert tier name to number"""
        tier_mapping = {
            "free": 0,
            "bronze": 1,
            "silver": 2,
            "gold": 3,
            "platinum": 4
        }
        return tier_mapping.get(tier.lower(), 0)
    
    def _get_tier_features(self, product: Product, tier: str) -> List[str]:
        """Get features for specific tier"""
        try:
            if product.features and tier.lower() in product.features:
                return product.features[tier.lower()]
            return []
        except Exception as e:
            logger.error(f"Failed to get tier features: {e}")
            return []
